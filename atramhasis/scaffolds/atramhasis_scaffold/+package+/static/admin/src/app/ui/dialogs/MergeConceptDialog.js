define([
  'dojo/_base/declare',
  'dijit/_TemplatedMixin',
  'dijit/_WidgetsInTemplateMixin',
  'dijit/Dialog',
  'dojo/_base/array',
  'dojo/_base/lang',
  'dojo/topic',
  'dojo/promise/all',
  'dojo/dom-construct',
  'dgrid/OnDemandGrid',
  'dgrid/extensions/DijitRegistry',
  'dgrid/extensions/ColumnResizer',
  'dgrid/Selection',
  'dstore/Memory',
  'dstore/Trackable',
  'dojo/text!./templates/MergeConceptDialog.html'
], function (
  declare,
  _TemplatedMixin,
  _WidgetsInTemplateMixin,
  Dialog,
  array,
  lang,
  topic,
  all,
  domConstruct,
  OnDemandGrid,
  DijitRegistry,
  ColumnResizer,
  Selection,
  Memory,
  Trackable,
  template
) {
  return declare([Dialog, _TemplatedMixin, _WidgetsInTemplateMixin], {

    templateString: template,
    parentNode: null,
    baseClass: 'merge-concept-dialog',
    title: 'Merge concept or collection',
    scheme: null,
    concept: null,
    conceptSchemeController: null,
    _mergeGrid: null,
    _mergeStore: null,

    postCreate: function () {
      this.inherited(arguments);

      this.trackableMemory = declare([Memory, Trackable]);
      this._mergeStore = new this.trackableMemory({ data: [] });
      this._mergeGrid = this._createGrid({
        collection: this._mergeStore
      }, this.mergeConceptGridNode);
    },

    startup: function () {
      this.inherited(arguments);
      this._mergeGrid.startup();
    },

    hide: function () {
      this.inherited(arguments);
    },

    _createGrid: function(options, node) {
      var columns = {
        label: {
          label: ''
        },
        type: {
          label: '',
          formatter: function(value) {
            return value + ' match'
          }
        },
        link: {
          label: '',
          renderCell: function(object){
            if (object && object.uri) {
              return domConstruct.create('a', { href: object.uri, target: '_blank', title: object.uri,
                innerHTML: '<i class="fa fa-external-link"></i>' });
            }
          }
        }
      };

      var grid = new (declare([OnDemandGrid, DijitRegistry, ColumnResizer, Selection]))({
        collection: options.collection,
        columns: columns,
        selectionMode: 'single',
        showHeader: false,
        noDataMessage: '',
        loadingMessage: 'Fetching data..'
      }, node);

      grid.on('dgrid-error', function(event) {
        console.log(event.error.message);
      });

      return grid;
    },

    _okClick: function (evt) {
      console.debug('MergeConceptDialog::_okClick');
      evt.preventDefault();

      for (var id in this._mergeGrid.selection) {
        if (this._mergeGrid.selection[id]) {
          selected = this._mergeStore.getSync(id);
        }
      }

      if (selected) {
        this.emit('concept.merge', {
          conceptUri: selected.uri,
          concept: this.concept,
          schemeId: this.scheme
        });
        this.hide();
      } else {
        // do nothing
      }
    },

    show: function(concept, schemeId) {
      this.inherited(arguments);
      this.loadingMatchesContainer.style.display = 'inline-block';
      this.mergeGridContainer.style.display = 'none';
      this.concept = concept;
      this.scheme = schemeId;
      var promises = [];
      var matches = [];
      if (concept.matches) {
        for (var key in concept.matches) {
          if (!concept.matches.hasOwnProperty(key)) {
            continue;
          }
          var matchesList = concept.matches[key];
          array.forEach(matchesList, function(match) {
            promises.push(this.conceptSchemeController.getMatch(match, key).then(lang.hitch(this, function (matched) {
              var data = {
                id: matched.data.id,
                label: matched.data.label,
                uri: matched.data.uri,
                type: matched.type
              };
              matches.push(data);
            })));
          }, this);
        }
      }
      all(promises).then(lang.hitch(this, function() {
        this._mergeStore.setData(matches);
        this._mergeGrid.refresh();
        this.loadingMatchesContainer.style.display = 'none';
        this.mergeGridContainer.style.display = 'inline-block';
      }));
    },

    _cancelClick: function (evt) {
      console.debug('MergeConceptDialog::_cancelClick');
      evt.preventDefault();
      this.hide();
    }
  });
});
