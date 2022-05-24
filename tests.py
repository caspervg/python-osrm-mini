# -*- coding: utf-8 -*-
import unittest
try:
    from unittest import mock
except:
    import mock

try:
    from urllib.request import URLError
except:
    from urllib2 import URLError

from pandas import DataFrame
from geopandas import GeoDataFrame
import numpy
import os

import osrm


class MockReadable:
    def __init__(self, content):
        self.content = content

    def read(self):
        return self.content.encode('utf-8')


class TestOsrmWrapper(unittest.TestCase):
    def setUp(self):
        pass

    def test_helpers(self):
        _list = [i for i in osrm._chain([789, 45], [78, 96], [7878, 789, 36])]
        self.assertEqual(_list, [789, 45, 78, 96, 7878, 789, 36])

        p1 = osrm.Point(latitude=10.00, longitude=53.55)
        self.assertEqual(p1.longitude, p1[0])
        self.assertEqual(p1.latitude, p1[1])

    def test_RequestConfig(self):
        default_host = osrm.RequestConfig.host

        # Make a new RequestConfig object
        MyConfig = osrm.RequestConfig()
        MyConfig.host = "http://0.0.0.0:5000"  # Only change the host
        # ..so the profile and the version should remain unchanged
        self.assertEqual(str(MyConfig), "http://0.0.0.0:5000/*/v1/driving")

        # Make a new one by writing directly the pattern to use :
        MyOtherConfig = MyConfig("192.168.1.1/v1/biking")
        self.assertEqual(MyOtherConfig.profile, "biking")

        # Two equivalent ways are available to write the url pattern :
        MyOtherConfig2 = MyConfig("192.168.1.1/*/v1/biking")
        self.assertEqual(str(MyOtherConfig), str(MyOtherConfig2))

        # Parameters from the original RequestConfig object haven't changed:
        self.assertEqual(osrm.RequestConfig.host, default_host)

    @mock.patch('osrm.core.urlopen')
    def test_nearest(self, mock_urlopen):
        mock_urlopen.return_value = MockReadable(
            u"""{"waypoints":[{"distance":22064.816067,"hint":"YtOXh5LYdIgAAAAAAAAAAH0FAAAAAAAA-1IAAD2o_wUlqP8FbrcAAC6OdgIrck4BEL95AngUTwEAAAEBfDhq3w==","name":"","location":[41.324078,21.918251]}],"code":"Ok"}"""
            )
        result = osrm.nearest((41.5332, 21.9598))
        # nearest only return the parsed JSON response
        self.assertEqual(result["waypoints"][0]["distance"], 22064.816067)

    @mock.patch('osrm.core.urlopen')
    def test_simple_route(self, mock_urlopen):
        mock_urlopen.return_value = MockReadable(
            u'''{"code":"Ok","routes":[{"legs":[{"steps":[],"summary":"","duration":14821.6,"distance":256884.8}],"geometry":"a|wdCobf{F}|@h]}pC`dAmpAbh@qTvTob@d_@sJfEcQvBeJtJcGjNiM~Hqe@~Mcn@`P{i@vFgPn@}HtBeGz@{Md@gGxAoGhCwEh@y_@lBmM|@ac@dLsc@nJmh@|Jot@zEeUXoWtEsRpBmRd@o`@`Eab@fGka@nDYB|a@va@gDAyEmCoFqC}K_FkHqCy_@iNsLmEiFuB}EuBgHgDwC_BwCaBwFmD_@UqMcJkJ}H_JmImI_JiJyLwIgMaTm\\\\waBqiCqaAqxAwfDq`FszFeuH_tCyaEuVs[alAgtAoTcV`AcA|FsGl@k@dK{KxE_FzGoHb^k^lFgGxMkQxGwKjpAksBlGoKnNyW~Xyj@fh@gdAzRka@hCsGlJwVxGuVlL{g@|Jae@pS{~@jCqJfCuGnFwLxDuGtDaGvCwDtDyEfEcElzA{sAxKmKtH_IvFcInHuM`EgKjDuLxB_LxAgNx@uPA{U@sGJgGFiAAcDdA}KtBqLbGcS`m@ydBzTmk@hz@uqBnOm]~LeVlM_TfXcc@ncAe`BlKsQ|GuNnSyn@`]_gAfUis@tI}SjLgTzv@ccAv@W`LiNbh@ip@nOcSlK{Plr@}zA|Tmf@lTye@nUqf@jz@u{AfTk`@rGqObH}TdYyeAzRiu@vE_QbHsSfF_M`f@yiAvoAexCrTog@hOy_@rFgR`GwW?aBdp@{xCvlAsvDnJi\\\\|Fo\\\\xDs`@xRqiClBaW~Fio@Fg@bCaRpUmpAbDcR`EoUPuAdAyHtB}P\\\\qEf@_DZqDvCv@`rAl^fPnEbT`Hh@`@BBBBB?DBF?D?FCZDxtAbf@`GnBzt@lUbZjJvWfIvAd@~d@`ObEjA|JlEfAd@h~Ap{@dUrLjTzJb\\\\bIdNnBxTtA|\\\\Zds@mCbZj@j[bEvTtHn`@hMx}@nUjk@lPd^zNrcCleAl`@jOhYrFxpC`WbWnEhNfDfM~HjaAnn@nPdJvRdG|bDnx@nUtMxd@jYnw@ng@pr@j\\\\dRhKzNpIrKnL~Zx_@bW|\\\\fMpI|NjHnP`FhuC~j@~O`F~IhKpEpIr`@x|@vNb\\\\NXjLfU^r@`KxN`Q`MtQdJvvAxg@hC~@FBVH~DnArj@dQ~`@vJr_Bd[vc@tJle@`PfXfNfwBbqAhY|Rn`@|\\\\lZzUt\\\\bTnf@zU`VjRdL~OxMlYpUl`@vR`Wd]dQ~iCzz@hShKbb@`^fc@hUt\\\\pSbyA`cA`KlEvRlE|HiAzHaFjrBclB`PcJbQuFfRyDhS}ApPb@zMbCdR`FfRbJjSjRdLvQpEnLjHbTrKpd@pEhKlI~HvLdGtKpBlnHra@rP`CxMvCbiBjj@nOvJrPfN`K|R~IpSnDdQdA`WdQhjFjClOrEnLzHtJnOjHtl@hNjNb@nOgD~Id@bK|Hjn@`XjIrEdFlBpEnBbD|AvDnB`F|CnCfBbC`BfDnCfBvAxCjCfFzD|EhDfEjCxGrDrF|CfL|FhSnJfDjBvBf@~A^n@Vp@ThBd@x@\\\\`@Pj@Vt@`@X\\\\JNh@b@\\\\VxBhBx@l@d@Zp@f@|@jAxAnBbArAx@xAHRr@zAXp@CTBRLLNHR?BABCb@FhAPrE|@dJbB~FdBjBj@dGhBnA^rA`@pA`@h@JTD\\\\FxBj@fF|Aj@PzAb@rNhEPDxEvAlF~AVHrDdA~FfBt@XL]lq@afBdBaGb@qBtAuGFc@DKBMIY}BeBaXqZoB_FYyE@kHi@kE_Jg_@EkG?aKvAcRbAgFbDkHfCcIrQsg@dBwHvCmZjB}JpAqGNqF]oLc@}C_BkC{BwAwDgAwCqC{@}CaCoVUaYo@yFyCqPoBoDiHeIcBcDyCwM}CkOmBgGoCqG}EkJoX_h@_Qy[yAaHsDgWe@}CoAgDgDqEkb@}b@oB}CkGePgV}f@{CiEkF{E{XiPgHkFcBuCs@qCKyEjF{w@VyE?sIk@iG_CwV{Kmy@g@mEKsGvAktAbBc~Ar@u~@jAwfACwF_@cHg@wGsBqIcEsRsBuGoBiEeCoD}[o[uEiFiCgEwBgFo@{CsAcGoByJwFu[w@eDcB_HiDeMaBaHaCqNyAeJkAmM@kIVuUb@_[b@oSLaWr@_[d@oJrAaFI}X^kMTqLo@yHqCaMmAeG{@qJDcIZqGv@qKfE_p@V_DQ{BCcAiGi[g@gCc@oEMeEOiGiAsg@]{PeAek@","duration":14821.6,"distance":256884.8}],"waypoints":[{"hint":"YtOXh5LYdIgAAAAAAAAAAH0FAAAAAAAA-1IAAD2o_wUlqP8FbrcAAC6OdgIrck4BEL95AngUTwEAAAEBfDhq3w==","name":"","location":[41.324078,21.918251]},{"hint":"apH5jEvnv40AAAAAYAEAAAAAAAC_LQAA42gAAHZ5UQZhQk4IbrcAAFxqgAK9REQBFHOAAqgvRQFOAAEBfDhq3w==","name":"","location":[41.970268,21.251261]}]}'''
            )
        result = osrm.simple_route((41.5332, 21.9598), (41.9725, 21.3114),
                                   output="routes",
                                   geometry="wkt")

        # Only the "routes" part from the response should have be returned :
        self.assertIsInstance(result, list)

        # ... with geometry field transformed to WKT :
        self.assertIn("LINESTRING", result[0]["geometry"])

    @mock.patch('osrm.core.urlopen')
    def test_table_only_origins(self, mock_urlopen):
        mock_urlopen.return_value = MockReadable(
        u'''{"code":"Ok","durations":[[0,1559.9,4192.8,9858.4,7679.7],[1579.3,0,5300.6,8735.2,6507.6],[4214.7,5334,0,5671.5,3972.1],[9496.8,8354.6,5689.7,0,2643.2],[7270.1,6127.9,3971.5,2624.5,0]],"destinations":[{"hint":"-hmZhIIUJo8AAAAAAQAAAAoAAAAAAAAANwUAAP6jLAP9oywDbrcAAGdMQQF37oACaExBAXjugAIAAAEBfDhq3w==","name":"","location":[21.056615,42.004087]},{"hint":"P7yyg-Xnvo-GOH0ALAAAACYAAAAAAAAA-QAAAMut1QNf1AgDbrcAAIZRRgFrA4EChlFGAWsDgQIAAAEBfDhq3w==","name":"\xd0\x91\xd1\x83\xd0\xbb\xd0\xb5\xd0\xb2\xd0\xb0\xd1\x80 \xd0\x98\xd0\xbb\xd0\xb8\xd0\xbd\xd0\xb4\xd0\xb5\xd0\xbd","location":[21.385606,42.009451]},{"hint":"SzHlia8HEorwPf4AAQAAAFYAAAAAAAAA8wAAAIPVMgcv1TIHbrcAABfJPwF4rXkCGMk_AXmteQIAAAEBfDhq3w==","name":"R2231","location":[20.957463,41.528696]},{"hint":"VktjiIkUGY_-bPEACgAAAA8AAAAXAQAAWwQAAGHfwwb1cVUGbrcAAFqwQgFcqnICW7BCAVyqcgIJAAEBfDhq3w==","name":"R2347","location":[21.147738,41.069148]},{"hint":"dku7jXlLu43E7icBcQAAABYAAAAAAAAAAAAAAK8RqA-tEagPbrcAADXWSAEJAHcCNtZIAQkAdwIAAAEBfDhq3w==","name":"\xd0\xa2\xd1\x80\xd0\xb8\xd0\xb7\xd0\xbb\xd0\xb0","location":[21.550645,41.353225]}],"sources":[{"hint":"-hmZhIIUJo8AAAAAAQAAAAoAAAAAAAAANwUAAP6jLAP9oywDbrcAAGdMQQF37oACaExBAXjugAIAAAEBfDhq3w==","name":"","location":[21.056615,42.004087]},{"hint":"P7yyg-Xnvo-GOH0ALAAAACYAAAAAAAAA-QAAAMut1QNf1AgDbrcAAIZRRgFrA4EChlFGAWsDgQIAAAEBfDhq3w==","name":"\xd0\x91\xd1\x83\xd0\xbb\xd0\xb5\xd0\xb2\xd0\xb0\xd1\x80 \xd0\x98\xd0\xbb\xd0\xb8\xd0\xbd\xd0\xb4\xd0\xb5\xd0\xbd","location":[21.385606,42.009451]},{"hint":"SzHlia8HEorwPf4AAQAAAFYAAAAAAAAA8wAAAIPVMgcv1TIHbrcAABfJPwF4rXkCGMk_AXmteQIAAAEBfDhq3w==","name":"R2231","location":[20.957463,41.528696]},{"hint":"VktjiIkUGY_-bPEACgAAAA8AAAAXAQAAWwQAAGHfwwb1cVUGbrcAAFqwQgFcqnICW7BCAVyqcgIJAAEBfDhq3w==","name":"R2347","location":[21.147738,41.069148]},{"hint":"dku7jXlLu43E7icBcQAAABYAAAAAAAAAAAAAAK8RqA-tEagPbrcAADXWSAEJAHcCNtZIAQkAdwIAAAEBfDhq3w==","name":"\xd0\xa2\xd1\x80\xd0\xb8\xd0\xb7\xd0\xbb\xd0\xb0","location":[21.550645,41.353225]}]}'''
        )
        names = ['name1', 'name2', 'name3', 'name4', 'name5']
        coords = [[21.0566163803209, 42.004088575972],
                  [21.3856064050746, 42.0094518118189],
                  [20.9574645547597, 41.5286973392856],
                  [21.1477394809847, 41.0691482795275],
                  [21.5506463080973, 41.3532256406286]]
        durations, new_coords, _ = osrm.table(coords,
                                              ids_origin=names,
                                              output="pandas")
        self.assertIsInstance(durations, DataFrame)
        durations2, new_coords2, _ = osrm.table(coords,
                                                ids_origin=names,
                                                output="np")
        self.assertIsInstance(durations2, numpy.ndarray)
        self.assertEqual(durations.values.tolist(), durations2.tolist())

    @mock.patch('osrm.core.urlopen')
    def test_table_OD(self, mock_urlopen):
        mock_urlopen.return_value = MockReadable(
            u'''{"code":"Ok","durations":[[10785.3,9107,14619.6,5341.2],[9546.8,7934.9,15473,4054.3],[14559.4,12440.7,18315.9,9115.3],[14463.4,10768.4,22202.6,9904],[12236.7,8541.7,19975.9,7677.3]],"destinations":[{"hint":"XAiehPiqpY4_JQUAZQAAAA0BAACzBQAAVwEAALxM2gRcSLAIbrcAABnMXwGE7IAC2NBfASDugAINAAEBfDhq3w==","name":"1061","location":[23.055385,42.003588]},{"hint":"qdjCi1mz-4wAAAAAFgAAAAAAAABzEgAAKQgAABae8wfvnfMHbrcAAHmQVQErD4ECwJNVATgDgQK6AAEBfDhq3w==","name":"","location":[22.384761,42.012459]},{"hint":"lfafieL2n4kAAAAAAAAAADIAAABbAAAAPQYAAEz6EwdiWKIFbrcAADTGPwF-M5gC2Mg_AZgxmAIDAAEBfDhq3w==","name":"","location":[20.956724,43.529086]},{"hint":"8gQxizUOMYsAAAAAAAAAABsAAAAAAAAAQRkAANIcvgd1Hb4HbrcAADQQSQEqrn0CCNZIAdinfQIAAAEBfDhq3w==","name":"","location":[21.565492,41.791018]}],"sources":[{"hint":"-hmZhIIUJo8AAAAAAQAAAAoAAAAAAAAANwUAAP6jLAP9oywDbrcAAGdMQQF37oACaExBAXjugAIAAAEBfDhq3w==","name":"","location":[21.056615,42.004087]},{"hint":"P7yyg-Xnvo-GOH0ALAAAACYAAAAAAAAA-QAAAMut1QNf1AgDbrcAAIZRRgFrA4EChlFGAWsDgQIAAAEBfDhq3w==","name":"\xd0\x91\xd1\x83\xd0\xbb\xd0\xb5\xd0\xb2\xd0\xb0\xd1\x80 \xd0\x98\xd0\xbb\xd0\xb8\xd0\xbd\xd0\xb4\xd0\xb5\xd0\xbd","location":[21.385606,42.009451]},{"hint":"SzHlia8HEorwPf4AAQAAAFYAAAAAAAAA8wAAAIPVMgcv1TIHbrcAABfJPwF4rXkCGMk_AXmteQIAAAEBfDhq3w==","name":"R2231","location":[20.957463,41.528696]},{"hint":"VktjiIkUGY_-bPEACgAAAA8AAAAXAQAAWwQAAGHfwwb1cVUGbrcAAFqwQgFcqnICW7BCAVyqcgIJAAEBfDhq3w==","name":"R2347","location":[21.147738,41.069148]},{"hint":"dku7jXlLu43E7icBcQAAABYAAAAAAAAAAAAAAK8RqA-tEagPbrcAADXWSAEJAHcCNtZIAQkAdwIAAAEBfDhq3w==","name":"\xd0\xa2\xd1\x80\xd0\xb8\xd0\xb7\xd0\xbb\xd0\xb0","location":[21.550645,41.353225]}]}'''
            )
        origins = [[21.0566163803209, 42.004088575972],
                   [21.3856064050746, 42.0094518118189],
                   [20.9574645547597, 41.5286973392856],
                   [21.1477394809847, 41.0691482795275],
                   [21.5506463080973, 41.3532256406286]]
        destinations = [[23.0566, 42.004], [22.3856, 42.0094],
                        [20.9574, 43.5286], [21.5506, 41.7894]]

        durations, snapped_origins, snapped_destinations = \
            osrm.table(origins, destinations)

        self.assertIsInstance(durations, numpy.ndarray)

        expected_shape = (len(origins), len(destinations))
        self.assertEqual(durations.shape, expected_shape)
        self.assertTrue(durations.any())

    def test_non_existing_host(self):
        Profile = osrm.RequestConfig("localhost/v1/flying")
        self.assertEqual(Profile.host, "localhost")
        with self.assertRaises(URLError):
            osrm.nearest((12.36, 45.36), url_config=Profile)
        with self.assertRaises(URLError):
            osrm.trip(
                [(13.38886, 52.51703), (10.00, 53.55), (52.374444, 9.738611)],
                url_config=Profile)
        with self.assertRaises(URLError):
            osrm.simple_route(
                (13.38886, 52.51703), (10.00, 53.55), url_config=Profile)
        with self.assertRaises(URLError):
            osrm.match(
                [(10.00, 53.55), (52.374444, 9.738611)], url_config=Profile)
        with self.assertRaises(URLError):
            osrm.table(
                [(10.00, 53.55), (52.374444, 9.738611)],
                [(10.00, 53.55), (52.374444, 9.738611)],
                url_config=Profile)

    @mock.patch('osrm.core.urlopen')
    def test_trips(self, mock_urlopen):
        mock_urlopen.return_value = MockReadable(
            u'''{"code":"Ok","trips":[{"legs":[{"steps":[],"summary":"","duration":507739.7,"distance":10016386.4},{"steps":[],"summary":"","duration":10035.7,"distance":281576.6},{"steps":[],"summary":"","duration":517625,"distance":10320096.1}],"geometry":"qbs~@ebywHjyiDnl_Ltt_Dwlj@nf_AhqhDuymBbdeM_eiFhr}Ff{tBbplCikVln|Bfw`BpgrEcre@jrjEz~dDne|KwnjAv`aBac~Ci{N}}mFbtnJqf{@fzOkqgDmitD{wpAtgaAahRv{kDeirGbmkFaxMfyeHqdmK|z}Joz~GjptAstxDlsjDgieIm~Oaf`ArvaAgwpHiecGq}xB`pe@kliFiupG}|nHtscAusyBekk@otaCqplFm}dPhe{HkyjAabr@ogE_tfBdxzBatrIiwwCwtmDagnRoacBkufCkjdBirvKtvEck~@ljnBcvqAg`Di~KxsmF_j|Brym@xIvlhAywrF|rtCixhAx~yBaj|GfpsC~{IzsyJohgAxobJig~EfppR{vXhmvF{vlDnmtGs~XdpeCazkFxj_DsbxCrnwFajnFzwdAandHn|`MgogIvsyBcb{FyiyAsxdChsyOklxCpgyCyvuCx|aGe_r@d}qK`zq@iiqKjcfBwluCtlr@wtrDnyiGi@ckKq|jCta~DuzgGxddB`q@vgjE}ljFtc~Culr@~nwFkm}K`dnFgrdArhxCgtwFlwkFyg~CfaYesfCdylDqrtG|}X_nvFp~}EejpRdhgAkkbJwwIk~yJlf|G{isCjwhAc~yB~jtFg}uCs|@ubgA`o|Bc}m@`zKqpmFhuqAteDbk}@sxmBhrwKamFxnfCbhdB`inR`acBn{wCvumDywzBporIp}D|{fBbbkA`gr@b{dPk_{HrwaCrblFtsyBvjk@||nHuscAjliFhupGp}xBape@fwpHhecG`f`AsvaAfieIl~OrtxDmsjDnz~GkptApdmK}z}J`xMgyeHdirGcmkF`hRw{kDzwpAugaAjqgDlitDpf{@gzOj}mFssnJre~Cd|NvljAcbaB{~dDoe|Kbre@krjEgw`BqgrEhkVmn|Bg{tBcplC~diFir}FtymBcdeMof_AiqhDut_Dvlj@","duration":1035400.4,"distance":20618059}],"waypoints":[{"waypoint_index":1,"location":[13.388799,52.517033],"name":"Friedrichstra\xc3\x9fe","hint":"eCEKgHudrorU0AAAEAAAABgAAAAGAAAAAAAAAF-UMQdJgZUDE_sAAP9LzACpWCEDPEzMAK1YIQMBAAEB9TrYrw==","trips_index":0},{"waypoint_index":2,"location":[10.000001,53.549986],"name":"Steinstra\xc3\x9fe","hint":"bb6sgjcQRYPD5wAACQAAABsAAAAAAAAAAAAAAL_wBApIJj8KE_sAAIGWmACiGzEDgJaYALAbMQMAAAEB9TrYrw==","trips_index":0},{"waypoint_index":0,"location":[51.251707,10.424888],"name":"","hint":"YgjCifUIwokAAAAA-wAAAAAAAADIuwAAAAAAADqQIgf4IoMBE_sAAPsJDgM4Ep8ArCsfA3OZlACJAAEB9TrYrw==","trips_index":0}]}'''
            )
        coords = [(13.388860,52.517037), (10.00,53.55), (52.374444,9.738611)]
        result = osrm.trip(coords, output = "only_index")
        self.assertIsInstance(result, list)
        self.assertIn("waypoint", result[0])
        self.assertIn("trip", result[0])

        result2 = osrm.trip(coords, geometry="WKT")
        self.assertIsInstance(result2, dict)
        self.assertIn("LINESTRING", result2['trips'][0]["geometry"])

    @mock.patch('osrm.core.urlopen')
    def test_matches(self, mock_urlopen):
        mock_urlopen.return_value = MockReadable(
            u'''{"code":"Ok","matchings":[{"confidence":0,"distance":8,"duration":1.1,"geometry":"g|j_Goro_CEO","legs":[{"steps":[],"summary":"","duration":1.1,"distance":8}]}],"tracepoints":[{"waypoint_index":0,"location":[21.05656,42.004042],"name":"","hint":"_BmZBOtFnIQAAAAABQAAABUAAAAAAAAAbQoAAIGx7AN-sewDbrcAADBMQQFK7oACWExBASDugAIAAAEBfDhq3w==","matchings_index":0},{"waypoint_index":1,"location":[21.056638,42.004072],"name":"","hint":"-xmZhP8ZmQQAAAAAAAAAABsAAAAAAAAAXwYAAAOkLAMBpCwDbrcAAH5MQQFo7oACnkxBAYTugAIAAAEBfDhq3w==","matchings_index":0}]}'''
            )
        coords = [[21.0566, 42.0040], [21.05667, 42.0041]]
        result = osrm.match(coords)
        self.assertIn("matchings", result)

    @unittest.skipIf("TRAVIS" in os.environ and os.environ["TRAVIS"] == "true",
                     "Test skipped on Travis")
    def test_sending_polyline(self):
        osrm.RequestConfig.host = "router.project-osrm.org"
        result1 = osrm.simple_route((41.5332, 21.9598), (41.9725, 21.3114),
                           output="routes",
                           geometry="wkt",
                           send_as_polyline=False)
        result2 = osrm.simple_route((41.5332, 21.9598), (41.9725, 21.3114),
                           output="routes",
                           geometry="wkt",
                           send_as_polyline=True)
        self.assertEqual(result1, result2)

if __name__ == "__main__":
    unittest.main()
