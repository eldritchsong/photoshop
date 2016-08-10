__author__ = 'brhoades'

import sys
from email.mime.text import MIMEText
import smtplib
from itertools import chain
import datetime
from string import Formatter

from utils import constants
from deploy import logger
from deploy import errors
from utils.yaml_cache import g_yaml_cache


class EmailGenerator(object):

    required_attrs = ['sender', 'recipients', 'subject', 'message']

    def __init__(self):
        self.host = constants.EMAIL[sys.platform]

        # init variables
        self._sender = None
        self._recipients = Receiver()
        self._message = None
        self._subject = None
        self._cache = g_yaml_cache

        self._header = None
        self._body = None
        self._footer = None

        self.logger = logger.init_logging(self)

        self._initialize()

    ######################################################################
    ## Public Functions

    @property
    def sender(self):
        return self._sender

    @sender.setter
    def sender(self, value):
        self._sender = value

    @property
    def recipients(self):
        return self._recipients

    @property
    def subject(self):
        return self._subject

    @subject.setter
    def subject(self, value):
        self._subject = value

    @property
    def header(self):
        return self._header

    @property
    def body(self):
        return self._body

    @property
    def footer(self):
        return self._footer

    ######################################################################
    # Private functions

    def _initialize(self):

        self._header = Header()
        self._body = Body(body_content='Stuff')
        self._footer = Footer(tool=self._cache.get('name'),
                              version=self._cache.get('version'),
                              timestamp=datetime.datetime.now().strftime('%H:%M:%S %Y/%m/%d'))

    def content(self):

        return ''.join((self.header.content(), self.body.content(), self.footer.content()))

    def send_message(self):

        for attr in self.required_attrs:
            if attr is None:
                raise errors.OperationError('Unable to send email, required attribute "{0}" is missing.'.format(attr))

        msg = MIMEText(self.content(), 'html')
        msg['Subject'] = self.subject
        msg['From'] = self.sender
        msg['To'] = ', '.join(self.recipients.to)
        msg['Cc'] = ', '.join(self.recipients.cc)

        s = smtplib.SMTP(self.host)
        s.sendmail(self.sender, self.recipients, msg.as_string())
        s.quit()

        return True


class Receiver(object):

    def __init__(self):
        self._to = list()
        self._cc = list()
        self._bcc = list()

    @property
    def to(self):
        return self._to

    @to.setter
    def to(self, value):
        if isinstance(value, list):
            self._to = value
        else:
            raise AttributeError('Expected to receive a list, instead recieved type {0}'.format(type(value)))

    @property
    def cc(self):
        return self._cc

    @cc.setter
    def cc(self, value):
        if isinstance(value, list):
            self._cc = value
        else:
            raise AttributeError('Expected to receive a list, instead recieved type {0}'.format(type(value)))

    @property
    def bcc(self):
        return self._bcc

    @bcc.setter
    def bcc(self, value):
        if isinstance(value, list):
            self._bcc = value
        else:
            raise AttributeError('Expected to receive a list, instead recieved type {0}'.format(type(value)))

    def __iter__(self):
        for attr in chain(self.to, self.cc, self.bcc):
            yield attr

    def __len__(self):
        return len(list(self.__iter__()))


class HTMLBaseObject(object):

    required_attrs = list()
    optional_attrs = list()
    content_enabled = True
    html = None

    def __init__(self, data=None, **kwargs):

        self._set_from_dict(data)

        if kwargs:
            for k, v in kwargs.iteritems():
                self.__dict__[k] = v

        for attr in self.optional_attrs:
            if not hasattr(self, attr):
                self.__dict__[attr] = None

        self.validate()

    def _set_from_dict(self, data):
        if isinstance(data, dict):
            for k, v in data.iteritems():
                self.__dict__[k] = v

    def validate(self):
        for attr in self.required_attrs:
            if not hasattr(self, attr):
                raise AttributeError('Unable to initialize object "{0}", '
                                     'missing required attribute "{1}".'.format(self.__class__.__name__, attr))

    def constructor(self):
        raise NotImplementedError

    def content(self):

        if self.content_enabled:
            key_dict = dict([(key, getattr(self, key)) for key in self.required_attrs if hasattr(self, key)])
            # validate
            for key in self.required_attrs:
                if not key_dict.get(key, False):
                    raise AttributeError('Missing required attribute "{0}"'.format(key))

            key_dict.update(dict([(key, getattr(self, key)) for key in self.optional_attrs if hasattr(self, key)]))

            return self.html.format(**dict([(key[1], key_dict.get(key[1], 'Unknown')) for key in Formatter().parse(self.html)]))

        raise NotImplementedError

    @property
    def data(self):
        return dict([(key, getattr(self, key, None)) for key in chain(self.required_attrs, self.optional_attrs)])


##########################################################################
# HTML Objects

class Header(HTMLBaseObject):

    html = """
           <html>
             <head>
             </head>
               <body style="-webkit-box-sizing: border-box;-moz-box-sizing: border-box;box-sizing: border-box;margin: 0;
                            font-family: &quot;Helvetica Neue&quot;,Helvetica,Arial,sans-serif;font-size: 14px;
                            line-height: 1.42857143;color: #333;background-color: #fff;">
                 <div class="container" style="width:1170px;padding-top: 15px;-webkit-box-sizing: border-box;
                                               -moz-box-sizing: border-box;box-sizing: border-box;padding-right: 15px;
                                               padding-left: 15px;margin-right: auto;margin-left: auto;">
                   <div class="jumbotron" style="padding: 15px 15px 15px 15px;-webkit-box-sizing: border-box;
                                                 -moz-box-sizing: border-box;box-sizing: border-box;margin-bottom: 30px;
                                                 color: inherit;background-color: #eee;border-radius: 6px;">
           """


class Footer(HTMLBaseObject):

    required_attrs = ['tool', 'version', 'timestamp']

    html = """
            </div>
                   <div class="row" style="-webkit-box-sizing: border-box;-moz-box-sizing: border-box;
                                           box-sizing: border-box;margin-right: -15px;margin-left: -15px;">
                     <div class="col-lg-12" style="-webkit-box-sizing: border-box;-moz-box-sizing: border-box;
                                                   box-sizing: border-box;position: relative;min-height: 1px;
                                                   padding-right: 15px;padding-left: 15px;width: 100%;">
                       <span class="text-muted" style="text-align: center;display: inherit;font-size: 0.9em;
                                                       padding-top: 5px;-webkit-box-sizing: border-box;
                                                       -moz-box-sizing: border-box;box-sizing: border-box;color: #777;">
                                                       This is an automatic email generated by {tool} {version}
                                                       </span>
                     </div>
                   </div>
                   <div class="row" style="-webkit-box-sizing: border-box;-moz-box-sizing: border-box;
                                           box-sizing: border-box;margin-right: -15px;margin-left: -15px;">
                     <div class="col-lg-12" style="-webkit-box-sizing: border-box;-moz-box-sizing: border-box;
                                                   box-sizing: border-box;position: relative;min-height: 1px;
                                                   padding-right: 15px;padding-left: 15px;width: 100%;">
                       <span class="text-muted" style="text-align: center;display: none!important;visibility: hidden;
                                                       font-size: 0.9em;padding-top: 5px;-webkit-box-sizing: border-box;
                                                       -moz-box-sizing: border-box;box-sizing: border-box;color: #777;">
                                                       [{timestamp}] End of message.
                                                       </span>
                     </div>
                   </div>
                 </div>
               </div>
             </body>
           </html>
           """


class Body(HTMLBaseObject):

    required_attrs = ['body_content']
    optional_attrs = ['report_name', 'report_type', 'report_title', 'report_subject']
    html = """
            <div class="row" style="-webkit-box-sizing: border-box;-moz-box-sizing: border-box;box-sizing: border-box;
                                    margin-right: -15px;margin-left: -15px;">
                <div class="col-lg-12" style="-webkit-box-sizing: border-box;-moz-box-sizing: border-box;
                                              box-sizing: border-box;position: relative;min-height: 1px;
                                              padding-right: 15px;padding-left: 15px;width: 100%;">
                    <span class="text-info h4" style="-webkit-box-sizing: border-box;-moz-box-sizing: border-box;
                                                      box-sizing: border-box;font-family: inherit;font-weight: 500;
                                                      line-height: 1.1;color: #31708f;margin-top: 10px;
                                                      margin-bottom: 10px;font-size: 18px;">
                        {report_name}
                    </span>
                    <span class="h4" style="-webkit-box-sizing: border-box;
                                            -moz-box-sizing: border-box;box-sizing: border-box;
                                            font-family: inherit;font-weight: 500;line-height: 1.1;
                                            color: inherit;margin-top: 10px;margin-bottom: 10px;
                                            font-size: 18px;">
                        for
                        <b style="-webkit-box-sizing: border-box;
                                  -moz-box-sizing: border-box;box-sizing: border-box;
                                  font-weight: 700;">
                            {report_type}
                        </b>
                    </span>
                </div>
            </div>
            <div style="padding: 5px 20px 20px;margin-right: 0;margin-left: 0;background-color: #fff;
                        border: 1px solid #ccc;border-radius: 4px 4px 0 0;-webkit-box-shadow: none;box-shadow: none;
                        -webkit-box-sizing: border-box;-moz-box-sizing: border-box;box-sizing: border-box;">
                <div class="row" style="display:table;clear:table;-webkit-box-sizing: border-box;
                                        -moz-box-sizing: border-box;box-sizing: border-box;margin-right: -15px;
                                        margin-left: -15px;">
                    <div class="col-lg-12" style="display:block;float:left;-webkit-box-sizing: border-box;
                                                  -moz-box-sizing: border-box;box-sizing: border-box;position: relative;
                                                  min-height: 1px;padding-right: 15px;padding-left: 15px;width: 100%;">
                        <h5 class="text-info" style="-webkit-box-sizing: border-box;-moz-box-sizing: border-box;
                                                     box-sizing: border-box;font-family: inherit;font-weight: 500;
                                                     line-height: 1.1;color: #31708f;margin-top: 10px;
                                                     margin-bottom: 10px;font-size: 14px;">
                            {report_subject}.
                        </h5>
                    </div>
                </div>
                <div class="row" style="clear:both;-webkit-box-sizing: border-box;
                                        -moz-box-sizing: border-box;box-sizing: border-box;margin-right: -15px;
                                        margin-left: -15px;">
                    <div class="col-lg-12" style="display:block;float:left;-webkit-box-sizing: border-box;
                                                  -moz-box-sizing: border-box;box-sizing: border-box;position: relative;
                                                  min-height: 1px;padding-right: 15px;padding-left: 15px;width: 100%;">
                        <p class="lead text-info" style="-webkit-box-sizing: border-box;-moz-box-sizing: border-box;
                                                         box-sizing: border-box;orphans: 3;widows: 3;margin: 0 0 10px;
                                                         margin-bottom: 15px;font-size: 21px;font-weight: 200;
                                                         line-height: 1.4;color: #31708f;">
                            <b style="-webkit-box-sizing: border-box;-moz-box-sizing: border-box;
                                      box-sizing: border-box;font-weight: 700;">
                                {report_title}
                            </b>
                        </p>
                    </div>
                </div>
            {body_content}
           """

    def __init__(self, data=None, **kwargs):
        self._elements = list()

        super(Body, self).__init__(data, **kwargs)

    def add_element(self, element):
        self._elements.append(element)

    def add_spacer(self):
        self._elements.append(TextElement(text=''))

    def content(self):
        body_content = str()
        for element in self.elements:
            body_content += '<br />' + element.content()

        self.__dict__['body_content'] = body_content

        return super(Body, self).content()

    @property
    def elements(self):
        return self._elements


##########################################################################
# HTML Elements

class HTMLElementBase(object):

    required_attrs = list()
    optional_attrs = list()
    has_constructor = True
    html = None

    def __init__(self, parent=None, **kwargs):

        self._parent = parent
        self._data = None

        for k, v in kwargs.iteritems():
            if k in chain(self.required_attrs, self.optional_attrs):
                self.__dict__[k] = v

        # todo: revise required attrs to a dictionary with a data type and default value
        # for attr in self.optional_attrs:
        #     if not hasattr(self, attr):
        #         self.__dict__[attr] = None

        self.validate()
        self.constructor()

    def validate(self):
        for attr in self.required_attrs:
            if not hasattr(self, attr):
                raise AttributeError('Unable to initialize object "{0}", '
                                     'missing required attribute "{1}".'.format(self.__class__.__name__, attr))

    @property
    def parent(self):
        return self._parent

    @property
    def data(self):
        return dict([(key, getattr(self, key, None)) for key in chain(self.required_attrs, self.optional_attrs)])

    def content(self):
        if isinstance(self._list_items(), dict):
            return self.html.format(**self._list_items())

        raise errors.OperationError('Content expected type dict, but received type {0}'.format(type(self._data)))

    def constructor(self):
        if self.has_constructor:
            raise NotImplementedError

    def _list_items(self):
        raise NotImplementedError


class TextElement(HTMLElementBase):
    required_attrs = ['text']
    optional_attrs = ['muted', 'bold', 'italic']
    has_constructor = False
    html = """
            <span style="{attributes}">{text}</span>
           """

    def _list_items(self):
        data = dict()
        css_reference = {'muted': 'color: #777;',
                         'bold': 'font-weight: 700;',
                         'italic': 'font-style: italic;'}
        data['attributes'] = ''.join([css_reference.get(key) for key in self.optional_attrs if getattr(self, key, False)])
        data['text'] = getattr(self, 'text')

        return data


class RowElement(HTMLElementBase):

    optional_attrs = ['column_count']
    html = """
           <div class="row" style="clear:both;display:inline;-webkit-box-sizing: border-box;-moz-box-sizing: border-box;
                                   box-sizing: border-box;margin-right: -15px;margin-left: -15px;">
                {columns}
            </div>
           """

    def __init__(self, parent=None, **kwargs):
        self._columns = list()

        super(RowElement, self).__init__(parent, **kwargs)

    def constructor(self):
        for _ in range(getattr(self, 'column_count', 0)):
            self._columns.append(ColumnElement(parent=self))

    def _list_items(self):
        return {'columns': ''.join(column.content() for column in self._columns)}

    def add_column(self, width=12):

        # validate width
        total_width = width
        for column in self.columns:
            total_width += int(column.column_size)

        element = ColumnElement(parent=self, column_size=width, text='')
        self._columns.append(element)

        if total_width > 12:
            # total width of all columns cannot exceed 12
            remainder = (total_width/12) % 12

            for column in self.columns:
                column.column_size = 12/remainder

        return element

    @property
    def columns(self):
        return self._columns


class ColumnElement(HTMLElementBase):

    required_attrs = ['column_size', 'text']
    has_constructor = False
    html = """
            <div style="display: {display};vertical-align: top;-webkit-box-sizing: border-box;
                        -moz-box-sizing: border-box;box-sizing: border-box;position: relative;
                        min-height: 1px;padding-right: 15px;padding-left: 15px;width:{column_size}%;">
                <span style="font-size: 14px;font-weight: 200;
                             line-height: 1.4;color: inherit;">
                    {text}
                </span>
            </div>
           """

    def _list_items(self):
        data = dict()
        data['text'] = getattr(self, 'text')
        data['column_size'] = 8.333333 * int(getattr(self, 'column_size'))
        data['display'] = 'inline' if self.index() else 'inline-block'

        return data

    def index(self):
        return self.parent.columns.index(self)


class TableElement(HTMLElementBase):

    optional_attrs = ['row_count', 'column_count']
    content_enabled = False
    html = """
           <table class="table table-bordered" style="font-family: verdana,arial,sans-serif;font-size: 11px;
                                                      -webkit-box-sizing: border-box;-moz-box-sizing: border-box;
                                                      box-sizing: border-box;border-spacing: 0;
                                                      border-collapse: collapse!important;background-color: transparent;
                                                      width: 100%;max-width: 100%;margin-bottom: 20px;
                                                      border: 1px solid #ddd;">
             {table_content}
           </table>
           """

    def __init__(self, parent=None, **kwargs):
        self._row_list = list()

        super(TableElement, self).__init__(parent, **kwargs)

    def constructor(self):
        for _ in range(getattr(self, 'row_count', 0)):
            self._row_list.append(TableRowElement(parent=self, column_count=getattr(self, 'column_count', 0)))

    def _list_items(self):
        return {'table_content': ''.join(row.content() for row in self.rows)}

    @property
    def rows(self):
        return self._row_list

    def add_row(self):
        row_element = TableRowElement(parent=self, column_count=0)
        self._row_list.append(row_element)
        return row_element


class TableColumnElement(HTMLElementBase):
    required_attrs = ['text', 'column_size']
    optional_attrs = ['weight', 'title']
    has_constructor = False

    html = """
           <td class="active" style="-webkit-box-sizing: border-box;-moz-box-sizing: border-box;
                                     box-sizing: border-box;padding: 0;background-color: {background}!important;
                                     border: 1px solid #ddd!important;padding: 8px;line-height:1.42857143;
                                     width:{column_size}%!important;">
             <span style="-webkit-box-sizing: border-box;-moz-box-sizing: border-box;
                       box-sizing: border-box;font-weight: {weight};">
               {text}
             </span>
           </td>
           """

    def __init__(self, parent=None, **kwargs):
        self._text_element = None

        super(TableColumnElement, self).__init__(parent, **kwargs)

    def _list_items(self):
        data = dict()
        data['weight'] = getattr(self, 'weight', 500)
        data['background'] = '#f5f5f5' if getattr(self, 'title', False) else '#fff'
        data['text'] = getattr(self, 'text')
        data['column_size'] = 8.333333 * int(getattr(self, 'column_size'))

        return data

    def add_text_element(self, **kwargs):
        element = TextElement(parent=self, **kwargs)
        self._text_element = element
        return element

    @property
    def text_element(self):
        return self._text_element


class TableRowElement(HTMLElementBase):

    required_attrs = ['column_count']
    html = """
           <tr style="-webkit-box-sizing: border-box;-moz-box-sizing: border-box;
                      box-sizing: border-box;page-break-inside: avoid;">
             {columns}
           </tr>
           """

    def __init__(self, parent=None, **kwargs):
        self._columns = list()

        super(TableRowElement, self).__init__(parent, **kwargs)

    def constructor(self):
        for _ in range(getattr(self, 'column_count')):
            self._columns.append(TableColumnElement(parent=self, text=''))

    def _list_items(self):
        return {'columns': ''.join(column.content() for column in self._columns)}

    @property
    def columns(self):
        return self._columns

    def add_column(self, width=12):
        # validate width
        total_width = width
        for column in self.columns:
            total_width += int(column.column_size)

        column_element = TableColumnElement(parent=self, column_size=width, text='')
        self._columns.append(column_element)

        if total_width > 12:
            # total width of all columns cannot exceed 12
            remainder = (total_width/12) % 12

            for column in self.columns:
                column.column_size = 12/remainder

        return column_element

if __name__ == '__main__':

    full_row = RowElement()
    full_col1 = full_row.add_column(width=2)
    text1 = TextElement(text='This is just a test', muted=True)
    full_col1.text = text1.content()
    full_col2 = full_row.add_column(width=10)
    full_col2.text = 'Should be half the width'

    table = TableElement()
    row1 = table.add_row()
    col1 = row1.add_column()
    col1.text = 'Received Scenes'
    col1.title = True
    col1.weight = 700

    col2 = row1.add_column()
    col2.text = 'Expected Scenes'
    col2.title = True
    col2.weight = 700

    col3 = row1.add_column()
    col3.text = 'Total in Shotgun'
    col3.title = True
    col3.weight = 700

    row2 = table.add_row()

    col4 = row2.add_column()
    col4.text = '40'

    col5 = row2.add_column()
    col5.text = '40'

    col6 = row2.add_column()
    col6.text = '398'

    email_content = EmailGenerator()
    doc = email_content.body

    doc.add_element(full_row)
    doc.add_element(table)

    doc.report_subject = 'Work Complete'

    print email_content.content()