import json


class Response(object):
    def __init__(self, attributes=None):
        if attributes:
            self.attributes = attributes
        else:
            self.attributes = dict()
            self.attributes["text"] = None
            self.attributes["roomId"] = None
            self.attributes["markdown"] = None
            self.attributes["html"] = None
            self.attributes["files"] = list()

    @property
    def text(self):
        return self.attributes["text"]

    @text.setter
    def text(self, val):
        self.attributes["text"] = val

    @property
    def files(self):
        return self.attributes["files"]

    @files.setter
    def files(self, val):
        self.attributes["files"].append(val)

    @property
    def roomId(self):
        return self.attributes["roomId"]

    @roomId.setter
    def roomId(self, val):
        self.attributes["roomId"] = val

    @property
    def markdown(self):
        return self.attributes["markdown"]

    @markdown.setter
    def markdown(self, val):
        self.attributes["markdown"] = val

    @property
    def html(self):
        return self.attributes["html"]

    @html.setter
    def html(self, val):
        self.attributes["html"] = val

    def as_dict(self):
        ret = dict()
        for k, v in self.attributes.items():
            if v:
                ret[k] = v
        return ret

    def json(self):
        return json.dumps(self.attributes)
