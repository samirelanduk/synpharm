<%@ page import = "org.manage.*" %>

<%
	FalseMap falseMap;
	Interaction interaction;
	if (Utilities.validMapId(request, "id")) {
		falseMap = DatabaseAccess.getFalseMap(request.getParameter("id"));
    if (falseMap == null) {
  		response.sendRedirect("/manage/");
			interaction = null;
    } else {
			interaction = falseMap.getInteraction();
		}
	} else {
		response.sendRedirect("/manage/");
		falseMap = null;
		interaction = null;
	}
%>

<html>
  <head>
    <title><% out.print(falseMap == null ? "" : falseMap.getMapId()); %></title>
    <link rel="stylesheet" type="text/css" href="/manage/css/map.css">
  </head>
  <body>
    <h1>False Map: <% out.print(falseMap == null ? "" : "Interaction " +
     falseMap.getInteractionId() + " - "
      + falseMap.getPdbCode()); %></h1>

    <div id="back">
      <a href="/manage/mapinteractions.jsp">Back to Interactions</a>
    </div>

    <div class="section" id="interaction">
			<h2>Interaction <% out.print(falseMap == null ? "" : falseMap.getInteractionId()); %></h2>
      <table>
        <tr>
          <td>Interaction ID</td>
          <td><% out.print(falseMap == null ? "" : falseMap.getInteractionId()); %></td>
        </tr>
        <tr>
          <td>Ligand ID</td>
          <td><% out.print(falseMap == null ? "" : Utilities.enclose(
           "a",
           String.format(
            "href='http://www.guidetopharmacology.org/GRAC/LigandDisplayForward?ligandId=%d' target='_blank'",
            interaction.getLigandId()
           ),
           "" + interaction.getLigandId()
          )); %></td>
        </tr>
        <tr>
          <td>Target ID</td>
          <td><% out.print(falseMap == null ? "" : Utilities.enclose(
           "a",
           String.format(
            "href='http://www.guidetopharmacology.org/GRAC/ObjectDisplayForward?objectId=%d' target='_blank'",
            interaction.getTargetId()
           ),
           "" + interaction.getTargetId()
          )); %></td>
        </tr>
        <tr>
          <td>Species</td>
          <td><% out.print(falseMap == null ? "" : interaction.getSpecies()); %></td>
        </tr>
      </table>
    </div>

    <div id="pdb" class="section"><h2>PDB Link</h2><% out.print(falseMap == null ? "" : Utilities.enclose(
     "a",
     String.format(
      "href='http://www.rcsb.org/pdb/explore.do?structureId=%s' target='_blank'",
      falseMap.getPdbCode()
     ),
     "" + falseMap.getPdbCode()
    )); %></div>

		<div id="deletion" class="section">
			<h2>Deletion</h2>
			<form method="POST" action="delete_falsemap.jsp">
				<input type="hidden" name="interactionId" value="<% out.print(falseMap == null ? "" : falseMap.getInteractionId()); %>">
				<input type="hidden" name="pdbCode" value="<% out.print(falseMap == null ? "" : falseMap.getPdbCode()); %>">
				<input type="submit" value="Delete Blacklist Mark"></input>
			</form>
		</div>
  </body>
</html>
