""" Module pour analyser les informations de pays à partir d'un fichier cty.dat. """
import io
import os

class CTY:
    """ Parse Country information in cty.dat format
        Docs: https://www.country-files.com/cty-dat-format/
        From: hamradio package (https://pypi.org/project/hamradio/)
    """

    data = os.path.join (os.path.dirname (__file__), 'data', 'cty.dat')

    # After prefix, additional info can be appended enclosed in the
    # following suffix markup. We ignore those currently.
    suffixes = '()', '[]', '<>', '{}', '~~'

    def __init__ (self, filename):
        # pylint: disable=unused-variable
        self.exact_callsign = {}
        self.prefix         = {}
        self.prf_max        = 0
        self.countries      = {}
        country = None
        with io.open (filename, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip ()
                if country is None:
                    assert line.endswith (':')
                    line = line.rstrip (':')
                    l = [x.lstrip () for x in line.split (':')]
                    country, cq, itu, ctycode, lat, lon, gmtoff, pfx = l
                    self.countries [country] = True
                    end = False
                else:
                    # Docs say 'should' contain comma at the end on continuation
                    if line.endswith (';'):
                        line = line.rstrip (';')
                        end = True
                    line = line.rstrip (',')
                    pfxs = line.split (',')
                    for pfx in pfxs:
                        # discard any additional info at end of prefix
                        for s in self.suffixes:
                            s = s [0]
                            pfx = pfx.split (s, 1) [0]
                        if pfx.startswith ('='):
                            pfx = pfx.lstrip ('=')
                            if pfx not in self.exact_callsign:
                                self.exact_callsign [pfx] = (country, lat, lon)
                        else:
                            l = len (pfx)
                            self.prf_max = max(self.prf_max, l)
                            if pfx not in self.prefix:
                                self.prefix [pfx] = (country, lat, lon)
                    if end:
                        country = None
                        end     = False
    # end def __init__

    def callsign_lookup (self, callsign):
        """ Lookup callsign in cty.dat data
            Returns (country, lat, lon) or None if not found
        """
        if callsign in self.exact_callsign:
            return self.exact_callsign [callsign]
        for n in reversed (range (self.prf_max)):
            pfx = callsign [:n+1]
            if pfx in self.prefix:
                return self.prefix [pfx]
        return None, None, None
    # end def callsign_lookup

# end class CTY
