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
  window,
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
      var win = window.getBox();
      domStyle.set(this.menuContainer, 'height', win.h - 90 + 'px');
      domStyle.set(this.overlayContainer, 'height', win.h - 90 + 'px');
    },

    _toggleMenu: function(evt) {
      evt ? evt.preventDefault() : null;
      console.log("toggleMenu");
      if (this.menuOpen) {
        this._slideClose(evt);
        //domClass.remove(this.menuSlideButton, 'fa-chevron-right');
        //domClass.add(this.menuSlideButton, 'fa-chevron-left');
        //domClass.remove(this.mobileMenuSlideButton, 'mobile-legend-open');
        //domClass.add(this.mobileMenuSlideButton, 'mobile-legend-close');
        //this.menuSlideButton.title = 'Toon legende';
        //this.mobileMenuSlideButton.title = 'Toon legende';
        //this.mobileMenuSlideButton.innerHTML = 'Legende';
      } else {
        this._slideOpen(evt);
        //domClass.remove(this.menuSlideButton, 'fa-chevron-left');
        //domClass.add(this.menuSlideButton, 'fa-chevron-right');
        //domClass.add(this.mobileMenuSlideButton, 'mobile-legend-open');
        //domClass.remove(this.mobileMenuSlideButton, 'mobile-legend-close');
        //this.menuSlideButton.title = 'Verberg legende';
        //this.mobileMenuSlideButton.title = 'Verberg legende';
        //this.mobileMenuSlideButton.innerHTML = '<i class="fa fa-times"></i>';
      }
    },

    _slideOpen: function (evt) {
      //console.debug('SlideLegend::_slideOpen');
      evt ? evt.preventDefault() : null;
      domClass.remove(this.menuContainer, 'slidemenu-close');
      domClass.add(this.menuContainer, 'slidemenu-open');
      domClass.remove(this.overlayContainer, 'slideoverlay-close');
      domClass.add(this.overlayContainer, 'slideoverlay-open');
      this.menuOpen = true;
    },

    _slideClose: function (evt) {
      //console.debug('SlideLegend::_slideClose');
      evt ? evt.preventDefault() : null;
      domClass.remove(this.menuContainer, 'slidemenu-open');
      domClass.add(this.menuContainer, 'slidemenu-close');
      domClass.remove(this.overlayContainer, 'slideoverlay-open');
      domClass.add(this.overlayContainer, 'slideoverlay-close');
      this.menuOpen = false;
    }

  });
});