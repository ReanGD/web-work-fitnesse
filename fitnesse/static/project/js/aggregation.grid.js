function _CreateHeader(builds, url_base)
{
  var header = '<th></th>';
  for (var i=0; i<builds.length; i++) {
    var url = '"' + url_base + builds[i] + '/"';    
    header += '<th class = "cell-header"><a href=' + url + ' target="_blank">' + builds[i] + '</a></th>';
  }

  return '<thead><tr>' + header + '</tr></thead>';
}

function _CreateNameTd(title, is_suite) {
  return '<td class="' + (is_suite ? "cell-suite" : "cell-test") + '">' + title + '</td>';
}

function _CreateResultTd(url, is_success) {
  return '<td onclick="location.href=\'r/' + url + '/\'" class="' + (is_success ? "cell-success" : "cell-error") + '"></td>';
}

function _CreateBody(builds, tests)
{
  var rows = '';
  for (var suite_name in tests) {
    var suite_value = tests[suite_name];

    rows += ('<tr>' + _CreateNameTd(suite_name, true) + '<td></td>'.repeat(builds.length) + '</tr>');

    for (var test_name in suite_value) {
      var row = _CreateNameTd(test_name, false);
      for (var i = 0; i < suite_value[test_name].length; i++) {
        test_result = suite_value[test_name][i];
       
        if (test_result[0] != 0)
          row += _CreateResultTd(test_result[0], (test_result[1] == 1));
        else
          row += '<td></td>';
      }

      rows += ('<tr>' + row + '</tr>');
    }
  }

  return '<tbody>' + rows + '</tbody>';
}

function CreateGrid(builds, tests, url_base)
{
  var header = _CreateHeader(builds, url_base);
  var body = _CreateBody(builds, tests);
  $(".fit-aggregation").append('<table>' + header + body + '</table>');
}

