var ss = SpreadsheetApp.openById("ID");
var ss_merged = SpreadsheetApp.openById("ID");

function TotalsSheet() {
  var totaldata = [];
  var sheets = ss.getSheets();
  var totalSheets = sheets.length;
  var start_date = new Date("8/3/2020");
  var end_date = new Date("8/31/2020");

  for (var i=0; i < totalSheets; i++) {
    var sheet = sheets[i];
    var values = sheet.getRange(2,1,sheet.getLastRow(),sheet.getLastColumn()).getValues();

    for (var row in values) {
      if ((values[row][0] !=  "") && (start_date <= values[row][1] && values[row][1] <= end_date)) { 
        totaldata.push(values[row]);
      }
      else {
        continue;
      }
    }
  }
  return totaldata;
}

function Start() {
  
  var All = ss_merged.getSheetByName("Merged");
  
  if(All != null){
    All.clear();
  }
  else {
    All = ss_merged.insertSheet("Merged");
  }

  var totaldata = TotalsSheet();
  for (var i = 0; i < totaldata.length; i++) {
    All.appendRow(totaldata[i]);
  }
  Logger.log("Finished");
}
