define([
  'dojo/_base/declare',
  'dojo/_base/lang',
  'dojo/dom-construct',
  'dojo/dom-class',
  'dojo/text!./templates/SlideMenu.html',
  'dijit/_WidgetBase',
  'dijit/_TemplatedMixin',
  'dojo/topic',
  'dojo/on',
  'dojo/window',
  'dojo/dom-style'
], function (
  declare,
  lang,
  domConstruct,
  domClass,
  template,
  _WidgetBase,
  _TemplatedMixin,
  topic,
  on,
  wind,
  domStyle
) {
  return declare([_WidgetBase, _TemplatedMixin], {

    baseClass: 'atramhasis-slidemenu',
    templateString: template,
    layerService: null,
    menuOpen: false,
    parentMap: null,
    overlayContainer: null,
    _layerLegend: null,

    /**
     * Standaard widget functie.
     */
    postCreate: function () {
      this.inherited(arguments);
      console.debug('SlideLegend::postCreate');
      this._calculateMenuHeight();
      on(window, 'resize', lang.hitch(this, function() { this._calculateMenuHeight() }));
    },

    /**
     * Standaard widget functie.
     * Bouwt de header op.
     */
    startup: function () {
      console.debug('SlideLegend::startup');
      this.inherited(arguments);
    },

    _calculateMenuHeight: function () {
      var win = wind.getBox();
      var footerheight = 30;
      var headerheight = 60;
      domStyle.set(this.menuContainer, 'height', win.h - footerheight - headerheight + 'px');
      domStyle.set(this.overlayContainer, 'height', win.h - footerheight - headerheight + 'px');
    },

    _toggleMenu: function(evt) {
      evt ? evt.preventDefault() : null;
      console.log("toggleMenu");
      if (this.menuOpen) {
        this._slideClose(evt);
      } else {
        this._slideOpen(evt);
      }
    },

    _slideOpen: function (evt) {
      evt ? evt.preventDefault() : null;
      domClass.remove(this.menuContainer, 'slidemenu-close');
      domClass.add(this.menuContainer, 'slidemenu-open');
      domClass.remove(this.overlayContainer, 'slideoverlay-close');
      domClass.add(this.overlayContainer, 'slideoverlay-open');
      this.menuOpen = true;
    },

    _slideClose: function (evt) {
      evt ? evt.preventDefault() : null;
      domClass.remove(this.menuContainer, 'slidemenu-open');
      domClass.add(this.menuContainer, 'slidemenu-close');
      domClass.remove(this.overlayContainer, 'slideoverlay-open');
      domClass.add(this.overlayContainer, 'slideoverlay-close');
      this.menuOpen = false;
    }
  });
});