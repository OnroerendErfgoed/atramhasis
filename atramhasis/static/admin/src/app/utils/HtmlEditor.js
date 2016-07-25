define([
  'dojo/_base/declare',
  'dojo/_base/array',
  'dojo/_base/lang',
  'dojo/text!./templates/HtmlEditor.html',
  'dijit/Toolbar',
  'dijit/_TemplatedMixin',
  'dijit/_WidgetBase',
  'dijit/form/Button',
  'dijit/ToolbarSeparator'
], function (
  declare,
  array,
  lang,
  template,
  Toolbar,
  TemplatedMixin,
  _WidgetBase,
  Button,
  ToolbarSeparator
) {
  return declare([_WidgetBase, TemplatedMixin], {

    templateString: template,
    editorToolbar: null,
    buttons: [
      {name: 'h4', icon: 'dijitEditorIconHeader dijitEditorIconH4', title: 'Header 4'},
      {name: 'h5', icon: 'dijitEditorIconHeader dijitEditorIconH5', title: 'Header 5'},
      {name: 'h6', icon: 'dijitEditorIconHeader dijitEditorIconH6', title: 'Header 6'},
      {name: 'emphasis', label: '', icon: 'dijitEditorIcon dijitEditorIconItalic', title: 'Italic'},
      {name: 'strong',  label: '', icon: 'dijitEditorIcon dijitEditorIconBold', title: 'Bold'},
      {name: 'link', label: '', icon: 'dijitEditorIcon dijitEditorIconCreateLink', title: 'Hyperlink'},
      {name: 'list', label: '', icon: 'dijitEditorIcon dijitEditorIconListBulletIndent', title: 'Lijst Toevoegen'},
      {name: 'addbibitem', label: '', icon: 'dijitEditorIcon dijitEditorIconInsertUnorderedList',
        title: 'Item Toevoegen'}
    ],
    htmlElements: [
      {key: 'h4', value: {name: 'h4', open: '<h4>', close: '</h4>'}},
      {key: 'h5', value: {name: 'h5', open: '<h5>', close: '</h5>'}},
      {key: 'h6', value: {name: 'h6', open: '<h6>', close: '</h6>'}},
      {key: 'emphasis', value: {name: 'emphasis', open: '<em>', close: '</em>'}},
      {key: 'strong', value: {name: 'strong', open: '<strong>', close: '</strong>'}},
      {key: 'link', value: {name: 'link', open: '<a href="#">', close: '</a>'}},
      {key: 'list', value: {name: 'list', open: '<ul>', close: '</ul>'}},
      {key: 'addbibitem', value: {name: 'addbibitem', open: '<li>', close: '</li>'}}
    ],

    postCreate: function () {
      this.inherited(arguments);
      this.editorToolbar = new Toolbar({}, this.containerToolbarNode);
    },

    startup: function () {
      this.inherited(arguments);
    },

    addButtons: function (btns) {
      array.forEach(btns, function (givenBtn) {
        array.forEach(this.buttons, function (btn) {
          if (btn.name === givenBtn) {
            if (givenBtn === 'separator') {
              var toolbarSeparator = new ToolbarSeparator({
                label: btn.title
              });
              this.editorToolbar.addChild(toolbarSeparator);
            } else {
              var button = new Button({
                name: btn.name,
                iconClass: btn.icon,
                title: btn.title,
                showLabel: false,
                onClick: lang.hitch(this, function () {
                  this._btnAction(btn.name);
                })
              });
              this.editorToolbar.addChild(button);
            }
          }
        }, this);
      }, this);
      this.editorToolbar.startup();
    },

    _btnAction: function (btn) {
      console.debug('HtmlEditor::_btnAction', btn);
      var textarea = this.containerTextAreaNode;
      var regex = /[^\n\r\v]+/gm;
      var elementValue = this._getHtmlElementByKey(btn);
      var open = elementValue.open;
      var close = elementValue.close;
      var position = textarea.scrollTop;
      var start = textarea.selectionStart;
      var end = textarea.selectionEnd;
      var first = textarea.value.substring(0, start);
      var last = textarea.value.substring(end, textarea.value.length);
      var val = textarea.value.substring(start, end);
      if(btn === 'addbibitem' && val !== '') {
        textarea.value = first + val.replace(regex, open + '$&' + close) + last;
      } else {
        textarea.value = first + open + val + close + last;
      }
      textarea.selectionStart = end + open.length + close.length;
      textarea.selectionEnd = end + open.length + close.length;
      textarea.scrollTop = position;
    },

    setContent: function (val) {
      this.containerTextAreaNode.value = val;
    },

    getContent: function () {
      return this.containerTextAreaNode.value;
    },

    _getHtmlElementByKey: function(key) {
      var htmlElements = array.filter(this.htmlElements, function(item) {
        return item.key === key;
      });
      return htmlElements[0].value;
    }
  });
});