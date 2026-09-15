# -*- coding: UTF-8 -*-
import logging
import traceback
import time
from urllib.parse import quote
from curl_cffi import requests
import json
import re
from bs4 import BeautifulSoup
from util.spider_util import SpiderUtil

# curl_cffi 模拟浏览器 TLS 指纹，规避 403；用 Session 复用连接与 cookie（403 可试改 chrome124/chrome131）
IMPERSONATE = "chrome124"

LIST_URL = "https://news.mingpao.com/ins/%E5%8D%B3%E6%99%82%E6%96%B0%E8%81%9E/main"
REQUEST_TIMEOUT = 25

# CF_FORM_BODY：由 CF 挑战页内 JS 计算并 POST，无法在服务端生成。若 403：浏览器打开列表页 -> 通过验证 -> F12 -> Application -> Cookies 复制到 headers；若仍 403 且出现挑战页：Network 里对该 URL 的 POST -> Copy as cURL -> 取 --data-raw 替换此处。
CF_FORM_BODY = "e5720bd4a41027190da95c144f6076da790ce8597260f33647032afbeb9d4bd1=Zaoc1E_pksL0upq2H9bWJEH2kA_kSqYB2v.E0sQsp3A-1770443881-1.2.1.1-xuzDM2Z_NjrDo4433YIt_M8xEozbJhWouongW6A9UjZgZ83_Ei1SvR8KQQhaWecTZcIo4497gkh0WNEcLeI7VanlzapOHfYW3rwT8YD5fz1GyXXvHtVfeWiWQCLFfsH.tmjzcZj8HSUGirydJoC5Ej5KUDSPHscEtvk_tUQbSdCCxgqdvTuoaF_YWBFbrReYKH6l3w4n3GXQ3nvBmajKNiTbnoOFaPWAtx1vAD5I46KXLq0VEvKHPUxhvxEvq16MZzK3pNrX1KpK47XvqUu1WdCwpEZ86.cR.iXjP5rLGiyB6B_Wpr7vf8fxNEz7C8Eq41dwhcCnQy.xCMQGqFoXe3dJNklV2kVgOjJfwUqRklAlou1mYpDm_SIdwdzDYpamgogw7pnir0PB0QQOWOJadAjUDGbp__lfzSly4qa4VOQI6xuWEFBD7pkBDHqPz_vFFgdrJ2jx6ujp1LmpqqHvtJljcY4tgbItflULcJbmV.iGaJ_T39old_7iVXuzswUUSOkp5IxKZqbVuCB4nzZH.aeU9gKEvWyCaJEz6emiCpe_xH1zq4s47cnkFxTQWVZoSGzj1aVEuu3n3zgC02BKJRDZIxPUGnhdejfJET9ejeFDVJabSnjvOEup56gZrjBENBU3bChQIS5NQ8skspVqYDe9gWz1aHCUg5FLW32eXWppbSJ1y9fzmoZWFILnMSsudFY6dnfjlaIxLBTtKRILy1qQNOV8PG5WFtq2HsmaCiBImU9NCFgC53etZDpX.EePzSbLtnaSB6D0v3hPeel4wtHNobL3wML2QJRBJobvaYBQChjfioFymfYXI8bs6F1Uk0y0i9EHFFITdy1tlnCzk3iIYGXTyN9UJHy4ng_paPoAJDEKYcUwKgcNoUyRAPvJIxcGioLH_KkT4LFMG9S.DmLykjPd_sfU9QJJMQJAW182cJQGDTp3Q5A.PhwGIw7L1whTRjwG4DxTRuVU0QTJbWd_6jf2Bs2Jfw8J_TXQU3Ds7O36808nhtPSKzI4UiVzTYFR6IIITrTUpKRlCCoSfNVifTXqCEib1nsAI6Kb1Yb.e8EEaAzTmVNd5Kn30kwjGL3GuZBRhm2J6wIrhoGIGA&5de354c135bf5006965b1ea1c40ba6d7a6b654bbfed115d8f1c4f096278b28d1=jh1Ao3OrGdVT7y2bnm1DxfZqE0hARYuql6ms5KFmprs-1770443881-1.2.1.1-S2qPKpQr8x2rjXl0yKPimb2fzrkCHept7H_e2ITeT3zomGFMqXK2O2xIn1BLcDtDp.VShCfrrsncWFRl8ZoZHuWuNLgNK2XQUKfRJmepboqRIjbO4N60iNpHJZY1W2VYiYHXkATbEwLH68.WIX1liOm41VbuTLAs2MTNzWwYT6vevNYeBAhOAuhY.NbG_uRir6igTQ5pnzY.4nQPfPBsbJBeR4epnrL5lP1ETHfRnTcN0QKbv18TXbx19r0oFz5xUIC6bTMj6sVppP44b7Id1IzUBqMAamjohID389RTxBB2ZiICsG8iPYCdxSJHy._fOdoBZqU2D8C_pAwsArzXFhn.xeKcM_GxIq6xOMDu33a.d6R5XTsfIX75TOwvcrmK60NeXr8GHSVXc81kG6e44ZmATxP95n6H7Lc8Ki0b2LEvbPDCaCgBXkDYbd32qS.7viLJN7Md3qsCeytfe5I_O8M60HO_2Fx3bTtJ.4I6BSLwLlPyl.jqHidJZmthLb.Zg9LrU1iGMeZiijEnVv9.iNS8HZ6rnRW4cNnAyxqg52G5GQgB.uJNylcChuSxGbG_wA_GZ1tOHnkiR3DzURl6gQ0LlGuiJfhqsqGCVjZEXDfx7_YblBhbF6FgMQ6W_1wp5lV0ojx25rzSX898dn.mogANvKryACK_YF6MUPY.fdL4gHaqQ3FngapZdqjnZrWMbiBQEwvsAhAr5.8LD3A8Z1uIwaiPPjZ0sSKtFcvRMz8C3r5hAaDacbf4dUVkieD3Rzu.HvZgDIyg5CwYeUNV8hFcXBbIVkNGRWRZljjV3ie8H5305gIjyQf5qeCH_Sx10SREMhb6matgnJOh77vpdK02ssr2hG1AMd7MpeMf2c0eN5jH_eXVPqkYcwvIQPkfPa9Kws3QnSrl.FteuhMayRBOCBtQRz6k6zN.LJL3JLbT3EWITvblK39ykNl8ilIlHgDJkhL0BIkbKEE2LYMUABhA4lBwxx_S9xNC8IcYZ0rFNhMq.dNzLe0pb5On7Mz4pRzkm6C_7y00KvNzd.H9ICg76kQU7zJ_BImEqjLgOxCvEDqKMjJGfBqnyl2j7fxxFlAlokTQhliFpQYYSoX6ZTjg7f7rnb4DBbT0et8FlVPvk.5c_CA_4QOaE74542pJVUW1bEPKmv4RdIpAFxa.ygW0FhA_gmqK2p0K89zj5a8U095DAMaNpY5y0x8p9UfXq__SVr.WTAAg0I5yHBuFVIUmajWuYlFwOnOPgDi1EZ.ckdEzcQQgWdVMG4gVj34.sOVBFZgkemHY3jdQ5db3znia0ibSTCMU_stDHI5QJUdfzpK4IMByp5Wn4KduX3XoddNz0IrXSsT2qQc3t8syiiPptv1wSk1o3rYkDTv9HscdRKP5ENsQoRUewE4xXVxpOcHm73122upzbK__sUWMLOLzBrn.puipOzqCnkLHwiwnwQ7OZ61BcEuk_1ioMC.2ASP75wKn9DTOKGB9MuZ8JVsaUZv.Uo.pXy5DbVDWn201cMekuXFxAfrwnxm.E0yeQQOHYhfrGtUVxfEfgbxPTN7DKWs.eqrhFwp8U2ANEOURBjN.DGSFzCTNrlYzKCatu5nseSc0nok1q85xWCyE_tCA5qgaT_6nQQi9sfOGKuQYM8_wWS6tlbVHcb1WWX4FELJfsFfKIx_N3zFjlA7H7HkePzChSBGsDPE12HI96Hq7UpJ.cgDRjjaNiYuqDn.muDcdGq_9NmHOgusrQy6u.i3XnhuMVlo5U4ZO4cgng4BjjuVWkHKt9aBTSu6GzqVU0cItIi65d55BBVmjjGoCZOArV.RPNZeg8fNENAeUp._a.e7ck9IumP8Iw_YC6zMbuoXVGzmzFsJl9y1HufOA2nxy0Vl4Gy9Uuk6iKRdVfm0x4ACVHV_B2JIyaVrpH.54qAbhhSgUqV3RbaapgNFD0qF1bC14dQFRxsw3.khLNbHIuZC1ofK9ivplbbesAyprk76A5P2os2uDrhi15NyfgQOeDYjXi4JaItkuzCDn4lqWwVORBC30fWhADKpflehTCCa56E3lasvq9b9S.9RzAyNyRQo9fAEkgIWYHUEDKnyO7r1QUgwa_U1SD5Pp8dJxjalUxfzt.fdGgGPi0xvra_cbvAlLUy1vgIyhGiNWdIUIhxX0HuD6Vvp4xWF0rAfoooi7gjSIUJ1Qc.87NeHwhE42EvIfRpCAbaknnq1RLHURFXlRXsrr.Y3ucD71mN9jkeFfFmPFhb8zONkJe4YciJrcFp0vaCaRB7wxWzxhEOmfHFArszsP64CkA8ENisDme7PoLFtzJ.JRrwdAqvnodr2lsq6BwliAtRylVXQAeNWxF.51zshcyB2UqsJ.K67drxxalfmtKQ70kW3Hnj6_lsY56fUZQDj7mKl_mUCTniLgLXDK0kcEngYldIKzfE5ChKsLM52LodUP7vCVnS3px7JJ2JdNUE7oqIuv2G_Mt.HpWcKbBpcnQJXHIFmp2iZ1MP6T2nqhDwbyz2rXS79x9GzRPqnVbkHQ2eRxns.eaB4JkWhevoSUV58UiGgqKNykjAgxnde1Mqob4Gb8E1vbvcUHm9Whz11DTJLq.SHSGYgMvW3MUJ2L67h2r7W6rXjHTPcG6WiNA0KSLv3lv9WPCZeh.CYNGqLALOvRIy0YF66tk2FfpvmfLrKGeKf7vQFOPepMQtjraY28BufI2ISd0MIICVKgOJPTp2DVM9otDC0Tc.lMexp8UXL_WFiK00pjvjbdS76hh56YqN7XOhwGQG6nTcNK5tyBJ3dOGZKMBj1E0mxlyeJyoRp2vntVJl0rmElpX9YXr6zZc2RKyXizULlLTB5wiQLIut7v5O2_sYuR7mNgZN.hH4BKGz50UhAyevJmxc9qAeUSIRI4eNwFz_f7nY.1zJWCR0hQp696UKapZiOQJofQa7jU9V0Om36KtQLHNZmhpRc1Q3emiNOFmWOoPsSkEyJ3WIm8_TvyBWqPP.FaOjXPwFhikpz3gDS9UDdohH8STCAKHz0RjYv9TvSnT598rFZBSCuyzNmaEiSkUEKlPb51IwdObOM3WerSOL027tzFRkL8HkOIa0o23NIR0kxBbA4lQporFFi75T3U60eR6NDIVsS6dgar6kK2qv9z6Nz6RNbuBJ9CTDhq6ccynw.rrcqBpl2z4t4DDQEAatfwM1puN0nB2RIV7iLCU9SjS.prINCoMyNZAMme40cWwaFkOW.wfwnminzZ66VbRy9hZP6PPKXieLebSribUpqKLQE2mVyympLeoUjWbDu6g05YexBNLHoba3zY1dVxYh1f9FWldXh3Xh4eyAInz6dKiilZuMoyIt5jh0TsYTxt3U8MPvBeLKc6KnBZZ8VrtefPrlVWxbFxzlaU21lTuWu5fB4rgKDeqBG1VnplUq.99oFm3zxu3V0PtwTiIHwpzJ0E00kxDbevSNnuqhWqkdeVSb0RF_REsYPlwNHHIqLd.9IXd.tTvmfhMUHTdex44IANyYO00Z8Bk92q2d6nCc842CIgZX..X9W7uwXhCHQ6q8skcsDJqtpmYW73546t4b98HCXxO4fYLNpvzIHGX7rNcRAOIC.RDDx.fDIKooxW9EtNtEXhok_f2DIICpYvYKJ.CL8Ol3filLO_HhJNVRdbE4ZzTYUnmSkvwXVihUfA5bhnMgWbtUbtaCGct2G28xH4EzhU5zhkdIuGDtamDtE64RVpcfgDV.4TwVC8PTL3KaebaSAOrysg1Gf1QPz.tHTHmtRdx_kr0porFP6jnPu0jjlATuoz24.xA_MueSZSrro4ZGqs5d5yXJAMyKOQ4srGj675xJWA17IWYuhc3m9n7R646CX_0ANfyM41yAwklUuU4kezNuJARrBPgv43j5L0UpnURTGqLo6JxFYX5F2MG9ZatxYWrrRBEamSArcDGDOyLXeeRs4Tn4ZgawNWsbwf8imPk3aBajy__1X.4dgBj.b5XLpBxOzHby1mjEO13_0Y9Jxvfhcz.LSDck4Bogr62AznwPHIMyVXd8AV_UTj..jOoIAVOBOYMUhxQgauMGMZDQSauvkxI8Gqg.wzra3EFtCXNSzUsRrTgoRwX2Sq4QopvATxJIIGXLBCqevrkNUO5Ex6fxBT8.sjvSYoGq6O7TuYKxJWnB14ZEBnvNGB0S6qEDEBR6yj5trKSSenI4.p1ETcL97jn3utb.y1Bi41XYf_TD1Qj.kQyngJtifg_ba8Tj1FIe63OeuQa1NErrox0WCz8VZTq8uOsbAAtRiEcd1BFO4uq_ewgBpm2YCi8VjTgqStPRYcARI9s_tBw97dzOkMUXrLM2VczvCT_3uTjobxpUvcoSdTcNW9RZwGAoEzj5oDMYjcGp9L1EVOqBluZXXNuTjMMv6HoeEycaRTweTW57HAiExg8DjaR_Tcjx5qLQPCWkqJAzYvqjct5_xgaqIf1obwRfnHwCrbjx7_iu4rOjtm3hAFQX1AW0n74.Bf26s25VW2jw_hsNMckpHzYEzDUEFXALLNf3xu9GuIad0JmjT.fRqmFttF7bggyZRZnmcyIgKOal8T.qnYpBIVcf7i84rQt8J4kFuFP3tc2PH_u0u7xexwoteqb9mDsOe0oIWNGFeXYpnWKlGz_L9AAkn_XJwxpZwL1mxBXEMJQBJuUmB4rJZAZWySDztF5t9o4eJ76k5jHs1daURTVszXWMfXvhknWuQONMRzpogBHMD5TItaBFUVu.9rt2rriOJHsNkYLw2m0YDL8eOYaqdtyynu7J9cIO5GzwsORcSsSlFty8bPNME0dEZOS_rYEufur1oDhS0v6lq_rrwt3yGcR3lRtY7AqqnaEfJ2A9WIZprBrR0GD4RwP4ls06jV3hJRlEKg_mitxZgylKFISMr8IZ0D8oi1X2.vA3gJY9sjUlO_tZdd_nptXNLAEKpfFB8yUResaPiNRG8lXqAx0Tq9Ua56LAIL_30oz.BjzcPoTdTo6Ryh9d9tw.rIZDihiVsT7SdIBz2QRFfAtxwDWPiAKYud4u1ChdOhuXUDzsrIDP.kS1U73rb1hy2wz7kkLgeEubj9F47vDgLKJ.NOvstLNp7SBXUQcvdxh8z356vK_PD_X3b9gEPqv8K6iuTrGl3t.ngLb4lLB_seV161Rxil4E1ZbIToNjnyr8s57rckUsnyfsBxANDdcQ_zxKx_SAEq4nkPJaIJJdA1wahns4FxrnWtm1UdK4qjSeV5AQFaRxRuFfz4UMlLSxSV.e3AZXm6F2ZPXBuugmBePSrzb2A9xVd7C0xTdyjPi5v1RRIbocVwG9E7XVlmfxQqolnO.yvoKqCBffcbF5f5SXQv_iHj0c0kyz0jwioBcBGYJ2PJEY84vr.umQNUUfuYOW7s7H_yRLZ9tb7JQgUqa4wZ1UTGygZ3KyLhOjTDqNBuCFvl5bMDFsYsg8FVCHCvPANDmS15VWtJQnjFTFzv7a4ZCQcslZmxwHGL7w.Q2.lL1QGG5uj3m5Ge9.Sok.X6BRY6CWaC.8e5drYX2UZSrIV6JeQewHPG0a0mrh0Thpv3vMMsSF9huYRFei7f3KmdG9Dql9aOC5Zde9aPv3oa8F7Mo2lTKuSrBWj8Fxe7nHtNukyZD4YZ9yLt53g2y99BRKxTAXaLImPlDohjYNcYtMCMd2mOSnvjqnirgpG16OPe5wGyNSiW9sfTMy.NU7MRr7rTAt6vPvryxt1uTYcocFNpaP1PW2E23KaOfuhsqf6IO27YKI9z_AQv.W0T1oP6j1Ojg0pL6zhVfXSUr1lmWxR9CLnP7aZY6QNT0igP2toDBvi0XNaGrTrBWPseR8bi3h5UNLD5aQ97vNB3MMy9CXMgGOWuJnie0SZFIf9_uPJbiAF.YcWv6bqBQW63jRieSDgxORnKiGxdFI2uxMAZ2yesC8wxdSK6WwSruWLlYurT1NpXqn14KXPznTxE4WMjmJNKBo.tdviJyXH9tYT2sKU5QjhMtUn7QCgrCG4e4Z1cMRP8RAJTUlo8EzsoUV3_AIFgJEo_d8fh7NqBUkwkwMONQvr62Zu1SuMMnCYYNKnFgNd4xTgimnZhELGFrLRhvGzP8lUC6TzlhFCZJ3bFHq8wQ49p4K0mqLiEQPQEvx0yPsy47GNZTg_qnpzT44e1vyqaa_VoyapcsbjJr7Jm23rPFix6AYHMCmCBbjidIkaatrE314mhLFf4OoT_74EAtJNw4VbXRnkMteZZ6BkuxD4XLuvmaf1y26.UWo6VzhIvWPR9TvUVdrjq.mtd36.1BYvB5TDYvSmM_j04UD2qAY2CbMkSeVLQFv3m0gZQeVTGfitRVWZNfE8wctkp96CFyKZHwMEMrtEIMB92CsnIpMsgKkj9WdFDuXFFPNul3wKTZNlxeQgSoqnSd.7Px6UyA90evLCjP9HfO0S5tD.otU5yMHpdfYeIhiGhxmJf1y2ZkaWQChYhNvmjeEFrQ1gYGf3jhyZ1i9U_.Naow6JeYUTB.SNPn.kQuEVDLjxSDV.4cyV9N9FFkK5Xp4EAajczAjlZI6LoBmZQ6reMxV_9qmHKjVw7x_iCwWlopDusYy4ApXaYU1d3Mly45Bw1avgFLlqs8oOiR3urcoO2lwG6DR0.AbP7PsIjtnL01PNA7ecZVBrk91R4THudx4o9m.Fu6BpihfqBpzvTRK4U8XKMQDsSXGHSDeZOV3RhNyGBwYWyg8RfCCbJ73syyAUyA0BXT5VFcqOA087VWlR1OSJF39Vsgns3MmG4kUjMh5bjPFeMl6ASdrfLzvYpYdRT1vb.FRVQ.wjsCoXTw_J7zoM2tjp260bcufFmB877Rcw4p2jshvpsJJHrBPmshxibJLH67Bx9D3jJc7Dblxs7FOzD7J6d4.23G41TNyAre_c2S32U9QIQE3P.CBqLLpfuJisNRaIf9rARgEqB2Gep6o2fGTRCOvdcFHVwnYW.Xcd6Bjf.eik4hajhW6SLy9RcX1kEdwbaTTYeukbNG8oKFue0erVf7jlt9PklosXuYQ4Jz1NbpPjDNTR7emfckwVSa0kohIgRAq.Aj38h8evsoZVnPVU5QwG4DNMEcbqAeeonmdqB9sM4nLvZtQFwB8WR8kzmx.6IjXGTk.FItxd2hUC.Xade6Oe7ddTwSX6hhRYEFa8G6avu.TLJmbkAtoTK6zmRCh3vl05rujeusyIDRdOIolKbZTiohnVqgtsYz1HREsl.vrFZhacuW0FAxckyZxF3hktVtP.mLlWJYdTXWMIpampFia.BbjA7rjduwKimIgf10tM4BkR5vsJsg8JieiUkTKtxCkEWqiWOdr_w2KudMoMpYh3D9xwQEB3gJ2ClYvAPYpVEoj4HotSwn_pAPhMWUkaLnL10W7769ej7mX6gUQdUn3fVfankVrLK4OypdKwVb5GkNjwijSFzB6fdl56_9NlOvEkB9U7FEshrdfG9uu8QGEKPVaWlmFdtTq4YMvW8TjBFW_PdHPNxqk.hk.YLx.VTbEVAlQcHH3q5lF.37hlwbXRcd4HN8moElM1O1wcpIUtKDacNetaJ6iQQ1fl3WKXSXn5MHv2GTP4xVVp074Wy8m4VHZ0F93n7LNVA9L8PdY1NniZTl7T9KrxPvdBAbnWVMxUUYPDZXwVRDblGPtONgk49skrqpE52nvCQ32AbzyIkS_gVQhC1rScfLOpFtezRtnYDUbrWP0WPBF5V6PvlFemRmiY8e1Pt6P00U4LbpEpSKipTVRZhmCAwInfLxtH7w47czYlpJH2VlWY0EAoHVPyDZG2ZjhoWE7ZH3m5H8Xj1felhnWDYnVa7NJozNfmeXX3bnYM0kitL8OV33caX1Wow3R0yvzyDp0fSpv8caAAqKKn2O8J9X1L5z_EpGAyOfCFLTcYeN22mCEvd5jVCCTHvcXO84M31cWkytM5NcrykuC6jmzBDWVcdcV_duDN.Tku3F5i9tRcIFaWTTxEM.rUObUGJVnRtxzspaw47SrYCcWjwEuprRDildDl3z31G4PGQofhXM6DcCqnHrgyEK6THT8BvuaKiYg5FmTIJDdcjQHBuu3hwSuin89aAA2pyC1eLav3K2lrps8ONpur58j01.iLjpjBP796vqiLGBSBUy6Gum3V2ZxmHhQ6f&36cb1b1b842bba7b27957f0e8b7697f75ba647ea7a419691c9689c7e89ffdf02=hGA5s4OEPPqaQuoPPvBxun2Qm8bsWMMKq4qDZk8zERg-1770443888-1.0.1.1-nafQhW6hpqNQgscZUDhzy0poqcnnxWA0FzMlZFYfRNuLixQHqnvvk1rSjpAbAGnedhzeXFSLNlcg_j.IRhEKsSJWKwtU9QEDWKL8ozMabfxhODiyPetPx2w_Pu5PCTKTNNg1pmn1mPxkme4Fqo5UTEnRPeQejTerSbYsqhVokyZnSkAQKyqCNAhB6NsL9trV"

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "zh-CN,zh;q=0.9",
    "cache-control": "max-age=0",
    "content-type": "application/x-www-form-urlencoded",
    "origin": "https://news.mingpao.com",
    "priority": "u=0, i",
    "referer": "https://news.mingpao.com/ins/%E5%8D%B3%E6%99%82%E6%96%B0%E8%81%9E/main",
    "sec-ch-ua": '"Not(A:Brand";v="8", "Chromium";v="144", "Google Chrome";v="144"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
    "cookie": "__qca=I0-1104478899-1770348934117; _sharedid=976fead9-c9b7-44ec-a044-9d9ee3976511; _sharedid_cst=zix7LPQsHA%3D%3D; cookiesession1=678A3E0D596565A8E111B65ECED23D6B; pbjs-unifiedid=%7B%22TDID%22%3A%22a763e53e-af7b-48a5-b5b1-3b3b637f3443%22%2C%22TDID_LOOKUP%22%3A%22TRUE%22%2C%22TDID_CREATED_AT%22%3A%222026-01-06T03%3A35%3A18%22%7D; pbjs-unifiedid_cst=zix7LPQsHA%3D%3D; ucf_uid=48571ec2-6bf9-4640-a602-be769de64793; FPID=FPID2.2.m2tYUVdFzFMyx3QxpubRM%2FSqQusD8CgkxZu7io5bO2s%3D.1770348918; _fbp=fb.1.1770348921492.359114454217106644; _cc_id=fa5c70c9325d0645349027e1fcf981b6; panoramaId_expiry=1770953726724; panoramaId=e38ad901c4bba664d859829be02316d53938ed400f9559ef69c4c115ee54c90c; panoramaIdType=panoIndiv; usprivacy=1---; _pubcid=5f454def-ec40-43c6-8ba8-440d29f0da2f; _sharedID=698df34f-8dcc-4f96-b4b6-5664539d66b3; _sharedID_cst=zix7LPQsHA%3D%3D; _ym_uid=1770348936945629069; jiyakeji_uuid=5da20240-030e-11f1-a2fa-751cf2f72061; mpLoginStatus=nologin; fpestid=p8oqnwUyJuSN_zx6lhBTKQlI0MX42U1jUgt1yxvvRqMoNwWKBBHmXNgVK1mBdrJQOTZTAQ; iUUID=97ef7bc5b01da355de5025c5d197b6f9; _ga_MT34BGMGMN=GS2.1.s1770349565$o1$g1$t1770350193$j60$l0$h0; _ga_FWRHJGBF7Y=GS2.1.s1770356063$o3$g0$t1770356891$j60$l0$h0; _ga_26L1K95RQX=GS2.1.s1770350176$o1$g1$t1770357987$j28$l0$h0; _ga_M7E3P87KRC=GS2.1.s1770348935$o1$g1$t1770358048$j60$l0$h1841050657; cf_clearance=K8uDXcIJiXfre.4XdKKp1kCp6QLFG6eo6bPLvtSJKiM-1770443888-1.2.1.1-Qx5PLkLlU0gWmKBDg40DaQRqMgTPSt8Hba8HrQZKvoSqVyJHe.bTlWnUfIrquKwtSSIt46sp92LakcGdKToi7TA_M2lmODJMJqs5bAtislaLxd7f1wOiBNz7XeSxFsnvzZ9H.5mYyPFkiHPjbvomgzDyLPAE1mfrM_gnIkzriwxIqYjRObcJQJFrIyzZ_jyxW4Yv7eSjjpUZ.7E.PfA8UbnPt91qBZg816W4ncl2k8I; cto_bidid=4S9OdV9KZFUlMkIxQ0RsWmsxb240bE5Sd0M0M3hONE1uQ0V0aGFZS0MxYzR5a3NNTzJGOTh3TEl3MnI5REtCWVNuUXhGUWRwRUQwWHBoMVppN1BTWmlsYlNyQmdINDZ0UUdORTJOJTJGbjgwOGlxVVU4YlklM0Q; FPLC=GiHt8EHeXz%2Ba5ke5Fk5%2Fum4l5Rww9tCBN5MW70YhN0ENZcSB5nUb2HixKSt%2BkeRXGIPwTKcXP5MyK%2B7OpDO%2Foe2I0nXm0i1ZsE4UaPQO%2BH1hEXOxihXfXL0M%2B%2FbfQg%3D%3D; FPGSID=1.1770773949.1770773949.G-E35W61CKGY.DjGHhnXiRGQjx21WMkWqkg; _gid=GA1.2.1075805574.1770773949; _gat_gtag_UA_4717822_6=1; __gads=ID=19d7a96e2daee949:T=1770348923:RT=1770773949:S=ALNI_MZ6NIYMPmWrT5ryDI9YDt7GJK6C-A; __gpi=UID=000011f4403ab08b:T=1770348923:RT=1770773949:S=ALNI_MajclS-_EPXIkG-C5JKT9lnkkMF_A; __eoi=ID=6ea876c88da8b33f:T=1770348923:RT=1770773949:S=AA-AfjYJdV_OBI7Rd4jPZPfBfvqr; FCNEC=%5B%5B%22AKsRol926A3K-0gdcd5MZEtie2bYbDEjPHaseKJ8VZ4k7ZILcxiMVsGX9fJVNEs_Cp38MrLGgkbHPCZB4ROFRcjBwh3OJDX8vwflau6GauXLbOL-LCbjuQLCVIdwMfLciE8Hw-LoWXJ5CRK_Zurg0FDH73xbtwW3sg%3D%3D%22%5D%5D; cto_bundle=c4qXyF9kdDdUdWlNSkQyYiUyRkdWQ2QlMkJ6WXJEcFlPTTN2YnZXeFBwZWJ2aUtQWVY2akxseUFwMHZJTncxSDB3Tll0WmpXcHdqQ2Q2R3pma1dEQUxMQWJwS0RhQ2xEQk4lMkZ0emZQVXZSODVTMjNyQmZURXdvelFad2JSVzBuUnpDQyUyRmVaN1dsQlFnTVNGRU90T2NDWWMlMkZGM1o0YW92WlZ4cTNvU09PeW1GYU1xS0p2dXIxTzkySm4zTzFyRzNzdVlmTG9vZXBa; _ga=GA1.2.1511455330.1770348918; _tfpvi=ODU1NTU3NTAtMDgyOC00ZDZiLTg0MWMtN2FiZjdiNDZkMDExIy05LTU%3D; _ga_2CX22RM6FV=GS2.1.s1770773947$o3$g1$t1770773962$j45$l0$h0; _ga_PJXF9C93DG=GS2.1.s1770773948$o3$g1$t1770773962$j46$l0$h1864043649; _ga_E35W61CKGY=GS2.1.s1770773948$o3$g1$t1770773962$j46$l0$h1684943890; FCCDCF=%5Bnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C%5B%5B32%2C%22%5B%5C%22cb10f195-e7a1-444f-a055-4ae94fb8e87d%5C%22%2C%5B1770348922%2C963000000%5D%5D%22%5D%5D%5D; _ym_uid_cst=znv0HA%3D%3D; _pubcid_cst=e4d0cA%3D%3D",
}

base_url = "https://news.mingpao.com"
filename = "./news/data/mingpao/list.json"
util = SpiderUtil()

# GET 列表页用：不含 content-type，避免被当成 POST
list_headers_get = {k: v for k, v in headers.items() if k != "content-type" and k != "origin"}


def _fetch_list_page(session):
    """先 GET，403 或挑战页再 POST。"""
    time.sleep(1.5)  # 略延后首请求，降低被 CF 判为脚本的概率
    r = session.get(
        LIST_URL, headers=list_headers_get, timeout=REQUEST_TIMEOUT, impersonate=IMPERSONATE
    )
    if r.status_code == 200 and "contentwrapper" in r.text and "cf-browser-verification" not in r.text.lower():
        return r
    r = session.post(
        LIST_URL, headers=headers, data=CF_FORM_BODY, timeout=REQUEST_TIMEOUT, impersonate=IMPERSONATE
    )
    return r


def get_detail(link, session=None):
    util.info("link: {}".format(link))
    if session is None:
        session = requests.Session(impersonate=IMPERSONATE)
    try:
        response = session.get(
            link, headers=list_headers_get, timeout=REQUEST_TIMEOUT, impersonate=IMPERSONATE
        )
        if response.status_code == 200:
            body = BeautifulSoup(response.text, "lxml")
            soup = body.find(class_="article_content")
            if soup is None:
                util.error("article_content not found: {}".format(link))
                return ""
            for element in soup.select("p[dir='ltr']"):
                element.decompose()

            # 移除 <iframe src="https://www.facebook.com/plugins/page.php?
            for element in soup.select("iframe[src*='facebook.com']"):
                element.decompose()

            # 正则匹配多个 \n\n\n\n\n\n\n 只保留一个 \n
            description = re.sub(r"\n\n+", "\n", str(soup).strip())
            return description
        else:
            hint = " (refresh cookie from browser)" if response.status_code == 403 else ""
            util.error("request: {} error: {}{}".format(link, response.status_code, hint))
            return ""
    except Exception as e:
        util.error("request error: {}".format(str(e)))
        return ""


def run():
    data = util.history_posts(filename)
    _articles = data["articles"]
    _links = data["links"]
    insert = False

    session = requests.Session(impersonate=IMPERSONATE)
    response = _fetch_list_page(session)
    if response.status_code != 200:
        msg = "list page error: {}".format(response.status_code)
        if response.status_code == 403:
            msg += " (refresh cookie/CF_FORM_BODY from browser, see script comment)"
        util.log_action_error(msg)
        return
    body = response.text
    soup = BeautifulSoup(body, "lxml")
    items = soup.select(".contentwrapper")
    data_index = 0
    for index, node in enumerate(items):
        if data_index > 4:
            break
        title_el = node.select_one(".title")
        item_el = node.select_one("figure a")
        if not title_el or not item_el or not item_el.get("href"):
            continue
        kind = title_el.text.strip()
        if kind not in ["地 產", "經 濟"]:
            continue
        link = item_el["href"].strip()
        if not link.startswith("http"):
            link = base_url.rstrip("/") + "/" + link.lstrip("/")
        if link in ",".join(_links):
            util.info("exists link: {}".format(link))
            break
        title = (item_el.get("title") or item_el.get_text(strip=True) or "").strip()
        if not title:
            continue
        description = get_detail(link, session)
        if description:
            insert = True
            _articles.insert(
                index,
                {
                    "title": title,
                    "description": description,
                    "link": link,
                    "pub_date": util.current_time_string(),
                    "source": "mingpao",
                    "kind": 1,
                    "language": "zh-HK",
                },
            )
            data_index += 1
    if len(_articles) > 0 and insert:
        if len(_articles) > 10:
            _articles = _articles[:10]
        util.write_json_to_file(_articles, filename)

if __name__ == "__main__":
    # util.execute_with_timeout(run)
    util.info("403 Forbidden")
