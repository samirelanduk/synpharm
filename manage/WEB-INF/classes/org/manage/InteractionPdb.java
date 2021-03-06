package org.manage;

public class InteractionPdb {

  private String mapId;
  private int interactionId;
  private String pdbCode;
  private boolean manuallyAdded;
  private boolean manuallyMarkedCorrect;
  private String hetId;
  private String[] bindingResidues;
  private String receptorChain;
  private int originalChainLength;
  private String bindSequence;
  private double proportionalLength;
  private int internalContacts;
  private int externalContacts;
  private double contactRatio;
  private String residueIds;


  public InteractionPdb(Object[] fields) {
    this.mapId = (String)fields[0];
    this.interactionId = (Integer)fields[1];
    this.pdbCode = (String)fields[2];
    this.manuallyAdded = (Boolean)fields[3];
    this.manuallyMarkedCorrect = (Boolean)fields[4];
    this.hetId = (String)fields[5];
    this.bindingResidues = ((String)fields[6]) == null ? null : ((String)fields[6]).split(", ");
    this.receptorChain = (String)fields[7];
    this.originalChainLength = fields[8] == null ? 0 : (Integer)fields[8];
    this.bindSequence = (String)fields[9];
    this.proportionalLength = fields[10] == null ? 0.0 : (Float)fields[10];
    this.internalContacts = fields[11] == null ? 0 : (Integer)fields[11];
    this.externalContacts = fields[12] == null ? 0 : (Integer)fields[12];
    this.contactRatio = fields[13] == null ? 0.0 : (Float)fields[13];
    this.residueIds = (String)fields[14];
  }


	public String getMapId() {
		return mapId;
	}


	public void setMapId(String mapId) {
		this.mapId = mapId;
  }


	public int getInteractionId() {
		return interactionId;
	}


	public void setInteractionId(int interactionId) {
		this.interactionId = interactionId;
	}


  public Interaction getInteraction() {
     return DatabaseAccess.getInteraction(this.interactionId);
  }


	public String getPdbCode() {
		return pdbCode;
	}


	public void setPdbCode(String pdbCode) {
		this.pdbCode = pdbCode;
	}


	public boolean isManuallyMarkedCorrect() {
		return manuallyMarkedCorrect;
	}


	public void setManuallyMarkedCorrect(boolean manuallyMarkedCorrect) {
		this.manuallyMarkedCorrect = manuallyMarkedCorrect;
	}


	public boolean isManuallyAdded() {
		return manuallyAdded;
	}


	public void setManuallyAdded(boolean manuallyAdded) {
		this.manuallyAdded = manuallyAdded;
	}


	public String getHetId() {
		return hetId;
	}


	public void setHetId(String hetId) {
		this.hetId = hetId;
  }


	public String[] getBindingResidues() {
		return bindingResidues;
	}


	public void setBindingResidues(String[] bindingResidues) {
		this.bindingResidues = bindingResidues;
  }


	public String getReceptorChain() {
		return receptorChain;
	}


	public void setReceptorChain(String receptorChain) {
		this.receptorChain = receptorChain;
  }


	public int getOriginalChainLength() {
		return originalChainLength;
	}


	public void setOriginalChainLength(int originalChainLength) {
		this.originalChainLength = originalChainLength;
	}


	public String getBindSequence() {
		return bindSequence;
	}


	public void setBindSequence(String bindSequence) {
		this.bindSequence = bindSequence;
  }


	public double getProportionalLength() {
		return proportionalLength;
	}


	public void setProportionalLength(double proportionalLength) {
		this.proportionalLength = proportionalLength;
	}


	public int getInternalContacts() {
		return internalContacts;
	}


	public void setInternalContacts(int internalContacts) {
		this.internalContacts = internalContacts;
	}


	public int getExternalContacts() {
		return externalContacts;
	}


	public void setExternalContacts(int externalContacts) {
		this.externalContacts = externalContacts;
	}


	public double getContactRatio() {
		return contactRatio;
	}


	public void setContactRatio(double contactRatio) {
		this.contactRatio = contactRatio;
	}


	public String getResidueIds() {
		return residueIds;
	}


	public void setResidueIds(String residueIds) {
		this.residueIds = residueIds;
  }
}
