/*
	Javascript widget om meerdere termen van 1 type te kunnen toevoegen aan een object.
	In het doelformulier wordt een div voorzien, die via deze code dynamisch gevuld zal worden met herhaalbare velden.
	Auteur: Bram Goessens <bram.goessens@rwo.vlaanderen.be>
	Auteur: Koen Van Daele <koen.vandaele@rwo.vlaanderen.be>
	Copyright: VIOE
*/

define(
	["dojo/_base/declare",
	 "dijit/_WidgetBase",
	 "dijit/_TemplatedMixin",
	 "dojo/_base/lang",
	 "dojo/dom-construct",
	 "dijit/form/ValidationTextBox",
	 "dijit/form/Button",
	 "dojo/text!./templates/FieldRepeater.html"
	 ],
function(
	declare,
	WidgetBase,
	TemplatedMixin,
	lang,
	domConstruct,
	ValidationTextBox,
	Button,
    template	) {
	return declare(
		"app/form/FieldRepeater",
		[WidgetBase, TemplatedMixin],
	{
	templateString: template,

	name: 'FieldRepeater',

	multiple: 'multiple',

	idMap: [],

	fieldMap: [],

	buttonMap: [],

	buildRendering: function() {
		this.inherited(arguments);
	},

	postCreate: function() {
		this._addNewRowAdder();
		this._addAdder();
		//this._addRow();
	},

	_addNewRowAdder: function() {
		var adder = this._getNewRowAdder();
		if (adder) {
			domConstruct.place(adder.domNode,this.buttonContainer,'last');
		}
	},

	_addAdder: function() {
		var adder = this._getNewAdder();
		if (adder) {
			domConstruct.place(adder.domNode,this.buttonContainer,'last');
		}
	},

	_onAddRow: function(evt) {
		this._addRow();
	},

	_addRow: function(value) {
		if (!value || value == null) {
			value = '';
		} else {
			value = String(value);
		}
		//Indien de waarde al aanwezig is, niet toevoegen.
		var aanwezig = dojo.filter(this.fieldMap,function(widget){
			return (widget.get('value') == value);
		},this);
		if (aanwezig.length > 0) { return; }
		var r = domConstruct.create(
			'div',
			{'class': 'rowContainer'},
			this.fieldContainer
		);
		var field = this._getNewField();
		domConstruct.place(field.domNode,r);
		field.set('value', value);
		// ID bijhouden.
		this.idMap.push(field.get('id'));
		dojo.connect(field,'onBlur',this, '_onAddRow');
		this.fieldMap.push(field);
		var button = new dijit.form.Button({
			showLabel: false, label: 'Delete', iconClass: 'toonDeleteKnop' });
		dojo.connect(button,'onClick',this, function(){
			this.fieldContainer.removeChild(r);
			this.idMap.splice(this.idMap.indexOf(field.get('id')),1);
			this.fieldMap.splice(this.fieldMap.indexOf(field),1);
			field.destroyRecursive();
		});
		this.buttonMap.push(button);
		domConstruct.place(button.domNode,r);
	},

	_getNewField: function() {
		return this.getNewField();
	},

	getNewField: function() {
		return new ValidationTextBox({name: 'veld'});
	},

	_getNewAdder: function() {
		return this.getNewAdder();
	},

	getNewAdder: function() {
		return false;
	},

	_getNewRowAdder: function() {
		return this.getNewRowAdder();
	},

	getNewRowAdder: function() {
		var button = new Button({label:'Nieuwe rij', iconClass: 'toonAddKnop'});
		dojo.connect(button,'onClick',this,'_onAddRow');
		return button;
	},

	clearRows: function() {
		dojo.forEach(this.fieldMap,function(item,idx){
			item.destroyRecursive();
		},this);
		this.fieldMap=[];
		dojo.forEach(this.buttonMap,function(item,idx){
			item.destroyRecursive();
		},this);
		this.buttonMap=[];
		dojo.query('div.rowContainer',this.fieldContainer).forEach(function(item){
			this.fieldContainer.removeChild(item);
		},this);
		this.idMap=[];
	},

	_setValueAttr: function( obj ) {
		console.log(obj);
		this.clearRows();
		// Eerst nagaan of er geen lege waarden in de array zitten en die verwijderen
		var safe = dojo.filter(obj,function(item){return (item != '');});
		dojo.forEach(safe,this._addRow,this);
		//Nog een lege rij toevoegen
		this._addRow('');
	},

	_getValueAttr: function() {
		var tmp = new dojo.NodeList();
		dojo.forEach(this.idMap, function(item) {
			tmp.push(dijit.byId(item).get('value'));
		});
		// Lege extra rij verwijderen
		tmp = dojo.filter(tmp,function(item){return (item != '');});
		return tmp;
	}

	});
});
