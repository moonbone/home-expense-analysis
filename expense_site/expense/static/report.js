/**
 * Created by maord on 09/11/2017.
 */

var table = document.getElementById("reportTable");
if (table != null) {
    for (var i = 0; i < table.rows.length; i++) {
        for (var j = 0; j < table.rows[i].cells.length; j++)
        table.rows[i].cells[j].onclick = function () {
            showDetails(this);
        };
    }
}

function showDetails(tableCell) {
    if (tableCell.id) {

        getParams= `cat=${tableCell.id.split("_")[0]}&monthsback=${tableCell.id.split("_")[1]}`
        
        document.getElementById('details_view').src = '/expense/details?'+getParams

    }
}