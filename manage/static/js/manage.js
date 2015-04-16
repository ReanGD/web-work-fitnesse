function load_form(e, self)
{
  if (self == undefined)
    self = $(this);
  if (e.preventDefault != undefined)
    e.preventDefault();
  self.tab('show');
  ajaxGet(self.attr('url'), function(content){
      $("#view").html(content);
  });
}

function init(e, default_tab)
{
  load_form(e, default_tab);
  $('#mainmenu>li>a').click(load_form);
  $('#index').click(function(e){load_form(e, $('#mainmenu>li>a:first'));});

  $(document).on('submit', '#id_form_add_edit', function(){
      ajaxPost(this.action, $(this).serialize(), function(data, status) {
        $("#dlg").html(data);
      });
      return false;
    });

  $(document).on('click', '.btn-form', function(e) {
        e.preventDefault();
        ajaxGet($(this).attr('url'), function(content){
          $("#dlg").html(content).modal('show');
        });
        return false;
    });
}