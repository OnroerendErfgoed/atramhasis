from pyramid.scaffolds import PyramidTemplate


class AtramhasisTemplate(PyramidTemplate):
    _template_dir = 'atramhasis_scaffold'
    summary = 'Create an Atramhasis implementation'


class AtramhasisDemoTemplate(PyramidTemplate):
    _template_dir = 'atramhasis_demo'
    summary = 'Create an Atramhasis demo'
