

function run() {
  var bot_id="botTOKEN";
  var ss = SpreadsheetApp.openById('ID');
  var sheet = ss.getSheets()[0];

  var column = getRange(sheet)[0];
  var size = getRange(sheet)[1];
  var start_row =2;
  var selected_columns = [3,7];
  var rng = getRanges(sheet, start_row, selected_columns, size);
  
  for(var row in rng[0]){
    if (rng[0][row][0]!='Telegram') {
      continue;
    }
    else if (rng[0][row][0]=='Telegram') {
      var link = rng[1][row][0];
      var url = getUrl(link, bot_id);
      var sheet_row=Number(row)+2;
      setSubscribers(sheet, url, column, sheet_row);
      Utilities.sleep(5000);
    };
  };
  
  setDate(sheet, column);
}

function setSubscribers(sheet, url, column, row) {
  try {

    var response = UrlFetchApp.fetch(url);
  
    if (response.getResponseCode()==200){
      var response_json=JSON.parse(response.getContentText());
      var subscribers=response_json["result"];
      sheet.getRange(row, column).setValue(subscribers);
    }
  } catch (e) {
    Logger.log(e);
    //sheet.getRange(row, column).setValue("NA"); 
  }
}

function setDate(sheet, column) {
  var date = new Date();
  var format_date=Utilities.formatDate(date, "GMT-0400", "yyyy-MM-dd");
  sheet.getRange(1, column).setValue(format_date);
}

function getUrl(chat_url, bot_id) {
  var chat_id="@"+chat_url.substring(13,);
  var url = "https://api.telegram.org/"+bot_id+"/getChatMembersCount?chat_id="+chat_id;
  return url;
}

function getRange(sheet) {
  var last_row = sheet.getLastRow();
  var last_column = sheet.getLastColumn();
  
  var result = [last_column+1, last_row+1];
  return result;
}

function getRanges(sheet, start_row, sel_cols, last_row){
  
  var columnRanges = [];
  for(var col in sel_cols){
    columnRanges.push("R" + start_row + "C" + sel_cols[col] + ":R" + last_row + "C" + sel_cols[col]);
  };
  
  //Get columns 
  var rangeOfColumns = sheet.getRangeList(columnRanges);
  
  var ranges = rangeOfColumns.getRanges();
  var valsForEachCol = [];
  for(range in ranges){
    valsForEachCol.push(ranges[range].getValues());
  };
  
  return valsForEachCol;
}
