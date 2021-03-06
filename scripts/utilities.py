import pg8000
import datetime
import os
import config
import math
import pygtop
import molecupy
from molecupy.structures import ResiduicStructure

def get_connection():
    conn = pg8000.connect(
     host=config.host,
     database=config.db,
     user=config.user,
     password=config.password
    )
    return conn


def get_live_connection():
    conn = pg8000.connect(
     host=config.livehost,
     database=config.livedb,
     user=config.liveuser,
     password=config.livepassword
    )
    return conn


def get_interactions_row_count(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM interactions;")
    rowcount = cursor.fetchone()[0]
    cursor.close()
    return rowcount


def get_interaction_ids_from_table(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT interactionId FROM interactions;")
    ids = [row[0] for row in cursor.fetchall()]
    cursor.close()
    return ids


def affinity_range_to_str(range_tuple):
    return str(range_tuple[0]) if len(range_tuple) == 1 else " - ".join(
     [str(val) for val in range_tuple]
    )


def interaction_object_to_dict(interaction):
    return {
     "interactionId": interaction.interaction_id(),
     "ligandId": interaction.ligand_id(),
     "targetId": interaction.target_id(),
     "species": interaction.species(),
     "type": interaction.interaction_type(),
     "action": interaction.action(),
     "affinityType": interaction.affinity_type(),
     "affinityValue": interaction.affinity_high(),
     "affinityRange": interaction.json_data["affinity"]
    }


def get_table_interaction_as_dict(interaction, connection):
    cursor = connection.cursor()
    cursor.execute(
     "SELECT * FROM interactions WHERE interactionId=%s",
     (interaction.interaction_id(),)
    )
    row = cursor.fetchone()
    dictionary = {
     "interactionId": row[0],
     "ligandId": row[1],
     "targetId": row[2],
     "species": row[3],
     "type": row[4],
     "action": row[5],
     "affinityValue": row[6],
     "affinityRange": row[7],
     "affinityType": row[8]
    }
    cursor.close()
    return dictionary


def add_interaction_to_table(interaction, connection):
    cursor = connection.cursor()
    now = datetime.datetime.now()
    dictionary = interaction_object_to_dict(interaction)
    dictionary["dateAdded"] = now
    dictionary["dateModified"] = now

    values = [dictionary[key] for key in [
     "interactionId",
     "ligandId",
     "targetId",
     "species",
     "type",
     "action",
     "affinityValue",
     "affinityRange",
     "affinityType",
     "dateAdded",
     "dateModified"
    ]]

    cursor.execute(
     """INSERT INTO interactions VALUES (
      %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
      );""", values
    )
    connection.commit()
    cursor.close()


def interaction_differs_from_table(interaction, connection):
    interaction_object_dict = interaction_object_to_dict(interaction)
    interaction_row_dict = get_table_interaction_as_dict(interaction, connection)
    for key in interaction_object_dict:
        if type(interaction_object_dict[key]) is float:
            if math.floor(interaction_object_dict[key]) != math.floor(interaction_row_dict[key]):
                return True
        else:
            if interaction_object_dict[key] != interaction_row_dict[key]:
                return True
    return False


def update_interaction(interaction, connection):
    now = datetime.datetime.now()
    dictionary = interaction_object_to_dict(interaction)
    dictionary["dateModified"] = now
    values = [dictionary[key] for key in [
     "ligandId",
     "targetId",
     "species",
     "type",
     "action",
     "affinityValue",
     "affinityRange",
     "affinityType",
     "dateModified",
     "interactionId"
    ]]
    cursor = connection.cursor()
    cursor.execute(
     """UPDATE interactions SET
      ligandId = %s,
      targetId = %s,
      species = %s,
      type = %s,
      action = %s,
      affinityValue = %s,
      affinityRange = %s,
      affinityType = %s,
      dateModified = %s WHERE interactionId=%s;""", values
    )
    connection.commit()
    cursor.close()


def remove_interaction_row_by_id(interaction_id, connection):
    cursor = connection.cursor()
    cursor.execute("DELETE FROM interactions WHERE interactionId=%s", (interaction_id,))
    connection.commit()
    cursor.close()


def get_interaction_ids_never_checked_for_pdbs(connection):
    cursor = connection.cursor()
    cursor.execute(
     "SELECT interactionId, targetId FROM interactions WHERE lastPdbCheck IS null;"
    )
    id_pairs = [(row[0], row[1]) for row in cursor.fetchall()]
    cursor.close()
    return id_pairs


def get_interaction_ids_already_checked_for_pdbs(connection):
    cursor = connection.cursor()
    cursor.execute(
     "SELECT interactionId, targetId FROM interactions WHERE lastPdbCheck IS NOT null ORDER BY lastPdbCheck;"
    )
    id_pairs = [(row[0], row[1]) for row in cursor.fetchall()]
    cursor.close()
    return id_pairs


def give_pdbs_to_interaction(interaction, pdbs, connection):
    now = datetime.datetime.now()
    cursor = connection.cursor()
    cursor.execute(
     "UPDATE interactions SET lastPdbCheck=%s WHERE interactionId=%s;",
     (now, interaction.interaction_id())
    )
    connection.commit()
    cursor.execute(
     "SELECT pdb FROM interaction_pdb_maps WHERE interactionId=%s",
     (interaction.interaction_id(),)
    )
    pdbs_already_assigned = [row[0] for row in cursor.fetchall()]
    cursor.execute(
     "SELECT pdb FROM false_maps WHERE interactionId=%s",
     (interaction.interaction_id(),)
    )
    blacklisted_pdbs = [row[0] for row in cursor.fetchall()]

    pdbs_assigned_now = []
    for pdb in pdbs:
        if pdb not in pdbs_already_assigned and pdb not in blacklisted_pdbs:
            pdbs_assigned_now.append(pdb)
            cursor.execute(
             "INSERT INTO interaction_pdb_maps VALUES (%s, %s, %s, false, false);",
             (str(interaction.interaction_id()) + pdb, interaction.interaction_id(), pdb)
            )
            connection.commit()
    cursor.close()
    return pdbs_assigned_now


def get_interaction_pdb_maps(connection):
    cursor = connection.cursor()
    cursor.execute(
     """
     SELECT
      interactions.targetId, interaction_pdb_maps.interactionId, interaction_pdb_maps.pdb,
      interaction_pdb_maps.hetId, interaction_pdb_maps.bindingResidues, interaction_pdb_maps.bindSequence,
      interaction_pdb_maps.manualCorrectMark, interaction_pdb_maps.receptorChain, interaction_pdb_maps.originalChainLength,
      interaction_pdb_maps.proportionalLength, interaction_pdb_maps.internalContacts,
      interaction_pdb_maps.externalContacts, interaction_pdb_maps.contactRatio, interaction_pdb_maps.residueIds
     FROM interaction_pdb_maps LEFT JOIN interactions ON
      interaction_pdb_maps.interactionId = interactions.interactionId;"""
    )
    interaction_pdb_maps = [{
     "targetId": row[0],
     "interactionId": row[1],
     "pdbCode": row[2],
     "hetId": row[3],
     "bindingResidues": row[4],
     "bindSequence": row[5],
     "manuallyMarkedCorrect": row[6],
     "receptorChain": row[7],
     "originalChainLength": row[8],
     "proportionalLength": row[9],
     "internalContacts": row[10],
     "externalContacts": row[11],
     "contactRatio": row[12],
     "residueIds": row[13]
    } for row in cursor.fetchall()]

    cursor.close()
    return interaction_pdb_maps


def give_pdb_map_het_code(interaction_id, pdb_code, het_id, connection):
    cursor = connection.cursor()
    cursor.execute(
     "UPDATE interaction_pdb_maps SET hetId=%s WHERE mapId=%s;",
     (het_id, str(interaction_id) + pdb_code)
    )
    connection.commit()
    cursor.close()


def give_pdb_map_bind_site(interaction_id, pdb_code, site, connection):
    cursor = connection.cursor()
    cursor.execute(
     "UPDATE interaction_pdb_maps SET bindingResidues=%s WHERE mapId=%s;", (
      ", ".join([residue.residue_id() for residue in site.residues()]),
      str(interaction_id) + pdb_code
     )
    )
    connection.commit()
    cursor.close()


def give_pdb_map_bind_sequence(interaction_id, pdb_code, sequence, chain_id,
 chain_length, proportional_length, internal_contacts, external_contacts,
 contact_ratio, residueIds, connection):
    cursor = connection.cursor()
    cursor.execute(
     """UPDATE interaction_pdb_maps SET
      bindSequence=%s,
      receptorChain=%s,
      originalChainLength=%s,
      proportionalLength=%s,
      internalContacts=%s,
      externalContacts=%s,
      contactRatio=%s,
      residueIds=%s
      WHERE mapId=%s;""", (
      sequence,
      chain_id,
      chain_length,
      proportional_length,
      internal_contacts,
      external_contacts,
      contact_ratio,
      residueIds,
      str(interaction_id) + pdb_code
     )
    )
    connection.commit()
    cursor.close()


def get_live_interaction_ids(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT sequenceId FROM sequences;")
    ids = [row[0] for row in cursor.fetchall()]
    cursor.close()
    return ids


def make_live_sequence_from_stage_map(interaction, pdb_map, het_name, stage_connection, live_connection):
    interaction_dict = interaction_object_to_dict(interaction)
    now = datetime.datetime.now()
    cursor = live_connection.cursor()
    locs = []
    for index, char in enumerate(pdb_map["bindSequence"]):
        if char.isupper():
            locs.append(index)
    length = (locs[-1] - locs[0]) + 1
    cursor.execute("""
     INSERT INTO sequences VALUES (
      %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
     );""", [
      pdb_map["interactionId"],
      interaction_dict["ligandId"],
      interaction_dict["targetId"],
      interaction.target().name(),
      interaction.target().name(strip_html=True),
      interaction.target().target_type(),
      interaction_dict["species"],
      interaction_dict["type"],
      interaction_dict["action"],
      interaction_dict["affinityValue"],
      interaction_dict["affinityRange"],
      interaction_dict["affinityType"],
      now,
      now,
      pdb_map["pdbCode"],
      het_name,
      pdb_map["hetId"],
      pdb_map["bindingResidues"],
      pdb_map["receptorChain"],
      pdb_map["originalChainLength"],
      pdb_map["bindSequence"],
      pdb_map["proportionalLength"],
      pdb_map["internalContacts"],
      pdb_map["externalContacts"],
      pdb_map["contactRatio"],
      pdb_map["residueIds"],
      length
     ])
    live_connection.commit()
    cursor.close()


def fill_out_other_tables(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT sequenceId, ligandId, pdb, hetId FROM sequences;")
    sequences = cursor.fetchall()
    print("Adding any ligands that might be needed...")
    for sequence in sequences[::-1]:
        cursor.execute("SELECT ligandId FROM ligands WHERE ligandId=%s;", (sequence[1],))
        if len(cursor.fetchall()) == 0:
            ligand = pygtop.get_ligand_by_id(sequence[1])
            mass = ligand.molecular_weight()
            if not mass:
                pdb = molecupy.get_pdb_remotely(sequence[2])
                if len(sequence[3]) == 1:
                    chain = pdb.model().get_chain_by_id(sequence[3])
                    mass = chain.mass()
                elif "," in sequence[3]:
                    chains = [pdb.model().get_chain_by_id(id_) for id_ in sequence[3].split(",")]
                    residues = []
                    for chain in chains:
                        residues += chain.residues()
                    ligand_ = ResiduicStructure(*residues)
                    mass = ligand_.mass()
                else:
                    ligand_ = pdb.model().get_small_molecule_by_id(sequence[3])
                    mass = ligand_.mass()
            cursor.execute("""
             INSERT INTO ligands VALUES (
              %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
             );""", [
              ligand.ligand_id(),
              ligand.name(),
              ligand.name(strip_html=True),
              ligand.ligand_type(),
              ligand.radioactive(),
              ligand.approved(),
              ligand.approval_source(),
              ligand.hydrogen_bond_acceptors(),
              ligand.hydrogen_bond_donors(),
              ligand.rotatable_bonds(),
              ligand.topological_polar_surface_area(),
              mass,
              ligand.log_p(),
              ligand.lipinski_rules_broken(),
              "#".join(ligand.synonyms()).replace("{", "#").replace("}", "$").replace("'", "''").replace(u'\u2010', "-")
             ])
            print("\tAdded %s" % str(ligand))
            connection.commit()

    cursor.execute("SELECT ligandId FROM ligands;")
    ligands = cursor.fetchall()
    print("Adding any database links that might be needed...")
    for ligand_row in ligands:
        ligand = pygtop.get_ligand_by_id(ligand_row[0])
        cursor.execute("SELECT accession FROM ligand_links WHERE ligandId=%s", (ligand.ligand_id(),))
        accessions = [row[0] for row in cursor.fetchall()]
        for db_link in ligand.database_links():
            if db_link.accession() not in accessions:
                cursor.execute("""
                 INSERT INTO ligand_links VALUES (
                  %s, %s, %s, %s
                 );""", [
                  db_link.accession(),
                  db_link.database(),
                  db_link.url(),
                  ligand.ligand_id()
                 ])
                connection.commit()
                print("\tAdded %s" % str(db_link))


def get_paths(app_name):
    current_dir = "/".join(os.path.realpath(__file__).split("/")[:-1])
    paths = {}
    paths["app_dir"] = current_dir + "/../" + app_name
    paths["class_dir"] = paths["app_dir"] + "/WEB-INF/classes"
    paths["jar_dir"] = paths["app_dir"] + "/WEB-INF/lib/postgresql-connector.jar"
    paths["java_dir"] = paths["class_dir"] + "/org/" + app_name
    #paths["tomcat_dir"] = "/var/lib/tomcat7/webapps/"
    #paths["servlet_dir"] = "/usr/share/tomcat7/lib/servlet-api.jar"
    paths["tomcat_dir"] = "/var/lib/tomcat/webapps/"
    paths["servlet_dir"] = "/usr/share/tomcat/lib/tomcat-servlet-3.1-api.jar"
    if not os.path.exists(paths["tomcat_dir"]):
        paths["app_dir"] = current_dir + "/../" + app_name
        paths["class_dir"] = paths["app_dir"] + "/WEB-INF/classes"
        paths["jar_dir"] = paths["app_dir"] + "/WEB-INF/lib/postgresql-connector.jar"
        paths["java_dir"] = paths["class_dir"] + "/org/" + app_name
        paths["tomcat_dir"] = "/usr/local/tomcat/webapps/"
        paths["servlet_dir"] = "/usr/local/tomcat/lib/servlet-api.jar"
    return paths


def get_sequence_ids_from_table(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT sequenceId FROM sequences;")
    ids = [row[0] for row in cursor.fetchall()]
    cursor.close()
    return ids


def get_sequence_as_dict(sequence_id, connection):
    cursor = connection.cursor()
    cursor.execute(
     "SELECT sequenceId, pdb, receptorChain, bindsequence, residueIds, targetName, species FROM sequences WHERE sequenceId=%s",
     (sequence_id,)
    )
    if cursor.rowcount == 0:
        cursor.close()
        return None
    else:
        row = cursor.fetchone()
        dictionary = {
         "sequenceId": row[0],
         "pdb": row[1],
         "chain": row[2],
         "sequence": row[3],
         "residueIds": row[4].split(","),
         "targetName": row[5],
         "species": row[6]
        }
        cursor.close()
        return dictionary


def regenerate_sequence(sequence_id, stage_connection, live_connection):
    stage_cursor = stage_connection.cursor()
    live_cursor = live_connection.cursor()
    live_cursor.execute("SELECT pdb FROM sequences WHERE sequenceId=%s", (sequence_id,))
    pdb = live_cursor.fetchall()[0][0]

    stage_cursor.execute(
     "SELECT hetId, bindingResidues, receptorChain, originalChainLength, bindSequence, proportionalLength, internalContacts, externalContacts, residueIds FROM interaction_pdb_maps WHERE mapId=%s",
     (sequence_id + pdb,)
    )
    if stage_cursor.rowcount == 1:
        row = stage_cursor.fetchone()
        dictionary = {
         "hetId": row[0],
         "bindingResidues": row[1],
         "receptorChain": row[2],
         "originalChainLength": row[3],
         "bindSequence": row[4],
         "proportionalLength": row[5],
         "internalContacts": row[6],
         "externalContacts": row[7],
         "residueIds": row[8]
        }
        if dictionary["bindSequence"]:
            dictionary["hetCode"] = dictionary["hetId"] if len(dictionary["hetId"]) == 1 or "," in dictionary["hetId"] else molecupy.get_pdb_remotely(
             pdb
            ).model().get_small_molecule_by_id(dictionary["hetId"]).molecule_name()
            locs = []
            for index, char in enumerate(dictionary["bindSequence"]):
                if char.isupper():
                    locs.append(index)
            length = (locs[-1] - locs[0]) + 1
            live_cursor.execute(
             """UPDATE sequences SET
              hetCode=%s,
              hetId=%s,
              bindingResidues=%s,
              receptorChain=%s,
              originalChainLength=%s,
              bindSequence=%s,
              proportionalLength=%s,
              internalContacts=%s,
              externalContacts=%s,
              residueIds=%s,
              dateModified=%s,
              sequenceLength=%s
              WHERE sequenceId=%s;""", (
              dictionary["hetCode"],
              dictionary["hetId"],
              dictionary["bindingResidues"],
              dictionary["receptorChain"],
              dictionary["originalChainLength"],
              dictionary["bindSequence"],
              dictionary["proportionalLength"],
              dictionary["internalContacts"],
              dictionary["externalContacts"],
              dictionary["residueIds"],
              datetime.datetime.now(),
              length,
              sequence_id
             )
            )
            live_connection.commit()
        else:
            print("Doing nothing - map no longer has sequence")
    else:
        print("Doing nothing")
    stage_cursor.close()
    live_cursor.close()


def delete_sequence(sequence_id, stage_connection, live_connection):
    stage_cursor = stage_connection.cursor()
    live_cursor = live_connection.cursor()

    stage_cursor.execute("SELECT mapId FROM interaction_pdb_maps WHERE interactionId=%s", (sequence_id,))
    mapIds = [row[0] for row in stage_cursor.fetchall()]
    for mapId in mapIds:
        pdb = mapId[-4:]
        stage_cursor.execute("INSERT INTO false_maps VALUES (%s, %s, %s)", (mapId, sequence_id, pdb))
        stage_connection.commit()
        stage_cursor.execute("DELETE FROM interaction_pdb_maps WHERE mapId=%s", (mapId,))
        stage_connection.commit()

    live_cursor.execute("DELETE FROM sequences WHERE sequenceId=%s", (sequence_id,))
    live_connection.commit()

    stage_cursor.close()
    live_cursor.close()
