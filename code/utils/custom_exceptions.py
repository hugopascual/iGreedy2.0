#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class AuthFileNotFound(Exception):
    pass

class RequestSubmissionError(Exception):
    pass

class FieldsQueryError(Exception):
    pass

class MeasurementNotFound(Exception):
    pass

class MeasurementAccessError(Exception):
    pass

class ResultError(Exception):
    pass

class IncompatibleArguments(Exception):
    pass

class InternalError(Exception):
    pass