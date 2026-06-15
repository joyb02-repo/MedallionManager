function doPost(e) {
  try {
    var requestData = JSON.parse(e.postData.contents);
    var action = requestData.action;
    
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    
    if (action === "fetchData") {
      // 1. FETCH MEDALLIONS TAB DATA
      var sheet = ss.getSheetByName("Medallions"); 
      var range = sheet.getDataRange();
      var values = range.getValues();
      var medallionList = [];
      
      // Index 0 = Row 1 (Header). Data starts exactly on Index 1 (Row 2)!
      for (var i = 1; i < values.length; i++) {
        var row = values[i];
        if (!row[0]) continue; 
        
        medallionList.push({
          "Medallion": String(row[0]).trim(),
          "Rarity": String(row[1]).trim(),
          "Value": String(row[2]).trim(),
          "Availability": String(row[3]).trim(),
          "Probability": String(row[4]).trim()
        });
      }
      
      // 2. FETCH MASTER_SHEET TAB DATA
      var masterSheet = ss.getSheetByName("master_sheet");
      var collectionValue = "$0";
      var medallionsCollected = "0 / 12";
      
      if (masterSheet) {
        var masterValues = masterSheet.getDataRange().getValues();
        // Checked against your master tab layout structure
        if (masterValues.length > 2) {
          collectionValue = String(masterValues[2][2]).trim();     // Column C (Index 2)
          medallionsCollected = String(masterValues[2][3]).trim(); // Column D (Index 3)
        } else if (masterValues.length > 1) {
          collectionValue = String(masterValues[1][2]).trim();     
          medallionsCollected = String(masterValues[1][3]).trim();
        }
      }
      
      var output = {
        "status": "success",
        "medallions": medallionList,
        "master_summary": {
          "CollectionValue": collectionValue,
          "MedallionsCollected": medallionsCollected
        }
      };
      
      return ContentService.createTextOutput(JSON.stringify(output))
        .setMimeType(ContentService.MimeType.JSON);
    }
    
  } catch(err) {
    return ContentService.createTextOutput(JSON.stringify({"status": "error", "message": err.toString()}))
      .setMimeType(ContentService.MimeType.JSON);
  }
}
