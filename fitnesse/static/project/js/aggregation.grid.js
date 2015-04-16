function _generateColumns(builds, url_base) {
  var colSuiteNameFormatter = function (row, cell, value, columnDef, dataContext) {
    var css_class = "";
    if (dataContext.parent == null)
      css_class = (dataContext._collapsed) ? "expand" : "collapse";
    else
      css_class = "test-name";
    return "<span class='toggle " + css_class + "'></span>&nbsp;" + value
  };

  var colBuildFormatter = function (row, cell, value, columnDef, dataContext) {
    return null;
  };

  var columns = [{id: "title", name: "", field: "title", width: 340, cssClass: "cell-title", formatter: colSuiteNameFormatter}];

  $.each(builds, function (i, build_number) {
    columns.push({
        id: i,
        name: '<a href="' + url_base + build_number + '/" target="_blank">' + build_number + '</a>',
        field: i,
        width: 34,
        formatter: colBuildFormatter
      });
  });

  return columns;
}

function _dataAggregationGridFill(builds, tests, out_data, out_cell_css)
{
  var i = 0;
  $.each(tests, function (suiteName, suiteValue) {
    var suite = (out_data[i] = {});

    suite["id"] = i;
    suite["parent"] = null;
    suite["title"] = suiteName;

    $.each(builds, function (build_it, build_number) {
      suite[build_it] = null;
    })

    i = i + 1;

    $.each(suiteValue, function (testName, testsValue) {
      var d = (out_data[i] = {});

      d["id"] = i;
      d["parent"] = suite;
      d["title"] = testName;
      
      out_cell_css[i] = {};
      $.each(testsValue, function (build_it, testValue) {
        if (testValue[0] != 0) {
          d[build_it] = testValue[0];
          is_success = (testValue[1] == 1);
          out_cell_css[i][build_it] = (is_success) ? "cell-success" : "cell-error";
        } else
          d[build_it] = null;
      })

      i = i + 1;
    })
  });
}

function _dataViewAggregationGridCreate(builds, tests, out_cell_css)
{
  var data = [];
  _dataAggregationGridFill(builds, tests, data, out_cell_css);

  var dataView = new Slick.Data.DataView({ inlineFilters: true });
  dataView.beginUpdate();
  dataView.setItems(data);
  dataView.setFilter(function (item) {
    if (item.parent != null)
      if (item.parent._collapsed)
        return false;
    return true;
  });
  dataView.endUpdate();

  return dataView;
}

function AggregationGridCreate(builds, tests, url_base)
{
  var cell_css = {};
  var dataView = _dataViewAggregationGridCreate(builds, tests, cell_css);

  var options = {
    editable: false,
    enableAddRow: false,
    enableCellNavigation: true,
    enableColumnReorder: false,
    asyncEditorLoading: false,
    enableTextSelectionOnCells: true
  };

  var columns = _generateColumns(builds, url_base);
  var grid = new Slick.Grid(".fitnesse-result-grid", dataView, columns, options);
  grid.setCellCssStyles("cell_css", cell_css);
  dataView.syncGridCellCssStyles(grid, "cell_css")

  grid.onClick.subscribe(function (e, args) {
    if ($(e.target).hasClass("toggle")) {
      var item = dataView.getItem(args.row);
      if (item) {
        item._collapsed = (!item._collapsed);
        dataView.updateItem(item.id, item);
      }
    } else {
      var cell = grid.getCellFromEvent(e);
      if (cell.cell > 0) {
        var col_name = grid.getColumns()[cell.cell].id;
        var id = grid.getDataItem(cell.row)[col_name];
        if (id != null)
          document.location.href = "r/"+id+"/";
      }
    }
    e.stopImmediatePropagation();
  });

  dataView.onRowCountChanged.subscribe(function (e, args) {
    grid.updateRowCount();
    grid.render();
  });

  dataView.onRowsChanged.subscribe(function (e, args) {
    grid.invalidateRows(args.rows);
    grid.render();
  });

  grid.gotoCell(0, 0, false);
}
