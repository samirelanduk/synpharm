<%@ page import = "org.bsdb.*" %>
<%@ page import = "java.util.*" %>
<%
long[] ligandTypeCounts = DatabaseAccess.getLigandTypeCounts();
Object[][] ligandMassDistribution = DatabaseAccess.getLigandMassDsitribution();
String[] ligandMassBins = new String[ligandMassDistribution.length];
long[] ligandMasses = new long[ligandMassDistribution.length];
for (int i = 0; i < ligandMassBins.length; i++) {
	ligandMassBins[i] = "'" + (String)ligandMassDistribution[i][0] + "'";
	ligandMasses[i] = (Long)ligandMassDistribution[i][1];
}
long[] ligandApprovalCounts = DatabaseAccess.getLigandApprovalCounts();
%>

<%@include file="/includes/start.html"%>
<title>Data and Statistics - BindSequenceDB</title>
<link rel="stylesheet" type="text/css" href="/css/charts.css">
<script src="https://code.highcharts.com/highcharts.js"></script>
<script src="https://code.jquery.com/jquery.min.js"></script>
<%@include file="/includes/bodytop.html"%>

<h1>Data and Statistics</h1>

<div id="ligand_stats">

	<div class="box">
		<div class="box_title">
			Ligands by Type
		</div>
		<div class="box_body">
			<div class="explanation">
				A breakdown of the ligands in the BSDB database by Guide to PHARMACOLOGY
				type.
			</div>
			<table class="boxtable">
				<tr>
					<td>
						<table class="datatable">
							<tr><td>Synthetic Organic</td><td><% out.print(ligandTypeCounts[0]); %></td></tr>
							<tr><td>Metabolite</td><td><% out.print(ligandTypeCounts[1]); %></td></tr>
							<tr><td>Natural Product</td><td><% out.print(ligandTypeCounts[2]); %></td></tr>
							<tr><td>Endogenous Peptide</td><td><% out.print(ligandTypeCounts[3]); %></td></tr>
							<tr><td>Other Peptide</td><td><% out.print(ligandTypeCounts[4]); %></td></tr>
							<tr><td>Inorganic</td><td><% out.print(ligandTypeCounts[5]); %></td></tr>
							<tr><td>Antibody</td><td><% out.print(ligandTypeCounts[6]); %></td></tr>
						</table>
					</td><td>

						<div id="ligandTypesChart" style="min-width: 310px; height: 400px; max-width: 600px; margin: 0 auto"></div>
						<script>
							var chart = new Highcharts.Chart({
				        chart: {
			            plotBackgroundColor: null,
			            plotBorderWidth: null,
			            plotShadow: false,
			            type: 'pie',
									renderTo: 'ligandTypesChart'
				        },
				        title: {
			            text: 'Ligand Types'
				        },
				        tooltip: {
			            pointFormat: '{series.name}: <b>{point.percentage:.1f}%</b>'
				        },
				        plotOptions: {
			            pie: {
		                allowPointSelect: true,
		                cursor: 'pointer',
		                dataLabels: {
	                    enabled: true,
	                    format: '<b>{point.name}</b>: {point.percentage:.1f} %',
	                    style: {
	                    	color: (Highcharts.theme && Highcharts.theme.contrastTextColor) || 'black'
	                    }
		                }
			            }
				        },
				        series: [{
			            name: 'Proportion',
			            colorByPoint: true,
			            data: [{
		                name: 'Synthetic Organic',
		                y: <% out.print(ligandTypeCounts[0]); %>
			            }, {
		                name: 'Metabolite',
		                y: <% out.print(ligandTypeCounts[1]); %>
			            }, {
		                name: 'Natural Product',
		                y: <% out.print(ligandTypeCounts[2]); %>
			            }, {
		                name: 'Endogenous Peptide',
		                y: <% out.print(ligandTypeCounts[3]); %>
			            }, {
		                name: 'Other Peptide',
		                y: <% out.print(ligandTypeCounts[4]); %>
			            }, {
		                name: 'Inorganic',
		                y: <% out.print(ligandTypeCounts[5]); %>
			            }, {
		                name: 'Antibody',
		                y:<% out.print(ligandTypeCounts[6]); %>
			            }]
				        }]
						  });
						</script>
					</td>
				</tr>
			</table>
		</div>
	</div>

	<div class="box">
		<div class="box_title">
			Ligands by Mass
		</div>
		<div class="box_body">
			<div class="explanation">
				A breakdown of the ligands in the BSDB database by mass.
			</div>
			<table class="boxtable">
				<tr>
					<td>
						<table class="datatable">
							<thead><th>Ligand Mass (Da)</th><th>Count</th></thead>
							<% for (int i = 0; i < ligandMassDistribution.length; i++) {
										out.println(String.format("<tr><td>%s</td><td>%d</td</tr>", ligandMassDistribution[i][0], ligandMassDistribution[i][1]));
							} %>

						</table>
					</td><td>
						<div id="ligandMassChart" style="min-width: 310px; height: 400px; max-width: 600px; margin: 0 auto"></div>
						<script>
					    var chart = new Highcharts.Chart({
					        chart: {
					            type: 'column',
											renderTo: 'ligandMassChart'
					        },
					        title: {
					            text: 'Ligand Mass Distribution'
					        },
					        xAxis: {
					            categories: [
												<% for (int i = 0; i < ligandMassDistribution.length; i++) {
															out.println(String.format("'%s',", ligandMassDistribution[i][0]));
												} %>
					            ],
					            crosshair: true
					        },
					        yAxis: {
					            min: 0,
					            title: {
					                text: 'Count'
					            }
					        },
					        tooltip: {
					            headerFormat: '<span style="font-size:10px">{point.key} Da</span><table>',
					            pointFormat: '<tr><td style="color:{series.color};padding:0">{series.name}: </td>' +
					                '<td style="padding:0"><b>{point.y}</b></td></tr>',
					            footerFormat: '</table>',
					            shared: true,
					            useHTML: true
					        },
					        plotOptions: {
					            column: {
					                pointPadding: 0.2,
					                borderWidth: 0
					            }
					        },
					        series: [{
					            name: 'Ligand Count',
					            data: <% out.print(Arrays.toString(ligandMasses)); %>

					        }]
					    });
						</script>
					</td>
				</tr>
			</table>
		</div>
	</div>

	<div class="box">
		<div class="box_title">
			Ligands by Approval Status
		</div>
		<div class="box_body">
			<div class="explanation">
				A breakdown of the ligands in the BSDB database by approval status.
			</div>
			<table class="boxtable">
				<tr>
					<td>
						<table class="datatable">
							<tr><td>Approved</td><td><% out.print(ligandApprovalCounts[0]); %></td></tr>
							<tr><td>Not Approved</td><td><% out.print(ligandApprovalCounts[1]); %></td></tr>
						</table>
					</td><td>
					<div id="ligandApprovalChart" style="min-width: 310px; height: 400px; max-width: 600px; margin: 0 auto"></div>
					<script>
						var chart = new Highcharts.Chart({
							chart: {
								plotBackgroundColor: null,
								plotBorderWidth: null,
								plotShadow: false,
								type: 'pie',
								renderTo: 'ligandApprovalChart'
							},
							title: {
								text: 'Ligand Approval'
							},
							tooltip: {
								pointFormat: '{series.name}: <b>{point.percentage:.1f}%</b>'
							},
							plotOptions: {
								pie: {
									allowPointSelect: true,
									cursor: 'pointer',
									dataLabels: {
										enabled: true,
										format: '<b>{point.name}</b>: {point.percentage:.1f} %',
										style: {
											color: (Highcharts.theme && Highcharts.theme.contrastTextColor) || 'black'
										}
									}
								}
							},
							series: [{
								name: 'Proportion',
								colorByPoint: true,
								data: [{
									name: 'Approved',
									y: <% out.print(ligandApprovalCounts[0]); %>,
									color: '#2ECC40'
								}, {
									name: 'Not Approved',
									y: <% out.print(ligandApprovalCounts[1]); %>,
									color: '#FF4136'
								}]
							}]
						});
					</script>
					</td>
				</tr>
			</table>
		</div>
	</div>

</div>

<div id="sequence_stats">

	<div class="box">
		<div class="box_title">
			Sequences by Target Type
		</div>
		<div class="box_body">
			<div class="explanation">
			</div>
			<svg>
			</svg>
		</div>
	</div>

	<div class="box">
		<div class="box_title">
			Sequences by Mass
		</div>
		<div class="box_body">
			<div class="explanation">
			</div>
			<svg>
			</svg>
		</div>
	</div>

	<div class="box">
		<div class="box_title">
			Sequence Contiguity by Target Type
		</div>
		<div class="box_body">
			<div class="explanation">
			</div>
			<svg>
			</svg>
		</div>
	</div>

</div>

<div id="aboutback">
	<a href="/about">Back to About</a>
</div>

<%@include file="/includes/bodybottom.html"%>
