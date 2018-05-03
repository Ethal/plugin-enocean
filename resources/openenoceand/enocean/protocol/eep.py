# -*- encoding: utf-8 -*-
from __future__ import print_function, unicode_literals, division, absolute_import
import os
import logging
from collections import OrderedDict
from bs4 import BeautifulSoup

import enocean.utils
from enocean.protocol.constants import RORG


class EEP(object):

    def __init__(self):
        self.num_profiles = 0
        self.init_ok = False
        self.telegrams = {}
        directory = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'eep')
        file_array = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                if (file.endswith('.xml')):
                    file_array.append(os.path.join(root,file))
        try:
            for file in file_array:
                logging.info('Loading profile file : ' + str(os.path.basename(file)))
                with open(file, 'r') as xml_file:
                    self.soup = BeautifulSoup(xml_file.read(), "html.parser")
                self.init_ok = True
                self.__load_xml()
                self.num_profiles += 1
            logging.info('Successfully loaded ' + str(self.num_profiles) + ' profiles !')
        except IOError:
            # Impossible to test with the current structure?
            # To be honest, as the XML is included with the library,
            # there should be no possibility of ever reaching this...
            logging.error('Cannot load protocol file!')
            self.init_ok = False

    def __load_xml(self):
        for telegram in self.soup.find_all('telegram'):
            for function in telegram.find_all('profiles'):
                for type in function.find_all('profile'):
                    rorg = enocean.utils.from_hex_string(telegram['rorg'])
                    func = enocean.utils.from_hex_string(function['func'])
                    typeidx = enocean.utils.from_hex_string(type['type'])
                    if rorg in self.telegrams :
                        if func in self.telegrams[rorg]:
                            if typeidx in self.telegrams[rorg][func]:
                                continue
                            else:
                                self.telegrams[rorg][func].update({typeidx : type})
                        else:
                            self.telegrams[rorg].update({func : {typeidx : type}})
                    else:
                        self.telegrams.update({rorg : {func : {typeidx : type}}})

    @staticmethod
    def _get_raw(source, bitarray):
        ''' Get raw data as integer, based on offset and size '''
        offset = int(source['offset'])
        size = int(source['size'])
        return int(''.join(['1' if digit else '0' for digit in bitarray[offset:offset + size]]), 2)

    @staticmethod
    def _set_raw(target, raw_value, bitarray):
        ''' put value into bit array '''
        offset = int(target['offset'])
        size = int(target['size'])
        for digit in range(size):
            bitarray[offset+digit] = (raw_value >> (size-digit-1)) & 0x01 != 0
        return bitarray

    @staticmethod
    def _get_rangeitem(source, raw_value):
        for rangeitem in source.find_all('rangeitem'):
            if raw_value in range(int(rangeitem.get('start', -1)), int(rangeitem.get('end', -1)) + 1):
                return rangeitem

    def _get_value(self, source, bitarray):
        ''' Get value, based on the data in XML '''
        raw_value = self._get_raw(source, bitarray)

        rng = source.find('range')
        rng_min = float(rng.find('min').text)
        rng_max = float(rng.find('max').text)

        scl = source.find('scale')
        scl_min = float(scl.find('min').text)
        scl_max = float(scl.find('max').text)

        return {
            source['shortcut']: {
                'description': source.get('description'),
                'unit': source['unit'],
                'value': (scl_max - scl_min) / (rng_max - rng_min) * (raw_value - rng_min) + scl_min,
                'raw_value': raw_value,
            }
        }

    def _get_enum(self, source, bitarray):
        ''' Get enum value, based on the data in XML '''
        raw_value = self._get_raw(source, bitarray)

        # Find value description.
        value_desc = source.find('item', {'value': str(raw_value)}) or self._get_rangeitem(source, raw_value)

        return {
            source['shortcut']: {
                'description': source.get('description'),
                'unit': source.get('unit', ''),
                'value': value_desc['description'].format(value=raw_value),
                'raw_value': raw_value,
            }
        }

    def _get_boolean(self, source, bitarray):
        ''' Get boolean value, based on the data in XML '''
        raw_value = self._get_raw(source, bitarray)
        return {
            source['shortcut']: {
                'description': source.get('description'),
                'unit': source.get('unit', ''),
                'value': True if raw_value else False,
                'raw_value': raw_value,
            }
        }

    def _set_value(self, target, value, bitarray):
        ''' set given numeric value to target field in bitarray '''
        # derive raw value
        rng = target.find('range')
        rng_min = float(rng.find('min').text)
        rng_max = float(rng.find('max').text)
        scl = target.find('scale')
        scl_min = float(scl.find('min').text)
        scl_max = float(scl.find('max').text)
        raw_value = (value - scl_min) * (rng_max - rng_min) / (scl_max - scl_min) + rng_min
        # store value in bitfield
        return self._set_raw(target, int(raw_value), bitarray)

    def _set_enum(self, target, value, bitarray):
        ''' set given enum value (by string or integer value) to target field in bitarray '''
        # derive raw value
        if isinstance(value, int):
            # check whether this value exists
            if target.find('item', {'value': value}) or self._get_rangeitem(target, value):
                # set integer values directly
                raw_value = value
            else:
                raise ValueError('Enum value "%s" not found in EEP.' % (value))
        else:
            value_item = target.find('item', {'description': value})
            if value_item is None:
                raise ValueError('Enum description for value "%s" not found in EEP.' % (value))
            raw_value = int(value_item['value'])
        return self._set_raw(target, raw_value, bitarray)

    @staticmethod
    def _set_boolean(target, data, bitarray):
        ''' set given value to target bit in bitarray '''
        bitarray[int(target['offset'])] = data
        return bitarray

    def find_profile(self, bitarray, eep_rorg, rorg_func, rorg_type, direction=None, command=None):
        ''' Find profile and data description, matching RORG, FUNC and TYPE '''
        if not self.init_ok:
            logging.error('EEP.xml not loaded!')
            return None

        if eep_rorg not in self.telegrams.keys():
            logging.error('Cannot find rorg in EEP!')
            return None

        if rorg_func not in self.telegrams[eep_rorg].keys():
            logging.error('Cannot find func in EEP!')
            return None

        if rorg_type not in self.telegrams[eep_rorg][rorg_func].keys():
            logging.error('Cannot find type in EEP!')
            return None

        profile = self.telegrams[eep_rorg][rorg_func][rorg_type]

        if eep_rorg == RORG.VLD or not command is None:
            # For VLD; multiple commands can be defined, with the command id always in same location (per RORG-FUNC-TYPE).
            eep_command = profile.find('command', recursive=False)
            # If commands are not set in EEP, or command is None,
            # get the first data as a "best guess".
            if not eep_command or command is None:
                return profile.find('data', recursive=False)

            # If eep_command is defined, so should be data.command
            return profile.find('data', {'command': str(command)}, recursive=False)

        # extract data description
        # the direction tag is optional
        if direction is None:
            return profile.find('data', recursive=False)
        return profile.find('data', {'direction': direction}, recursive=False)

    def get_values(self, profile, bitarray, status):
        ''' Get keys and values from bitarray '''
        if not self.init_ok or profile is None:
            return [], {}
        output = OrderedDict({})
        for source in profile.contents:
            if not source.name:
                continue
            if source.name == 'value':
                try:
                    output.update(self._get_value(source, bitarray))
                except:
                    continue
            if source.name == 'enum':
                try:
                    output.update(self._get_enum(source, bitarray))
                except:
                    continue
            if source.name == 'status':
                try:
                    output.update(self._get_boolean(source, status))
                except:
                    continue
        return output.keys(), output

    def set_values(self, profile, data, status, properties):
        ''' Update data based on data contained in properties '''
        if not self.init_ok or profile is None:
            return data, status

        for shortcut, value in properties.items():
            # find the given property from EEP
            target = profile.find(shortcut=shortcut)
            if not target:
                # TODO: Should we raise an error?
                logging.erroring('Cannot find data description for shortcut %s', shortcut)
                continue

            # update bit_data
            if target.name == 'value':
                data = self._set_value(target, value, data)
            if target.name == 'enum':
                data = self._set_enum(target, value, data)
            if target.name == 'status':
                status = self._set_boolean(target, value, status)
        return data, status
