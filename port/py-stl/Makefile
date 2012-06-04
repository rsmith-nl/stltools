# Ports collection makefile for: py-stl
# Date created:                  28 Dec 2011
# Whom:                          rsmith@xs4all.nl
#
# $FreeBSD$

PORTNAME=		py-stl
PORTVERSION=		3.1
CATEGORIES=		graphics python
MASTER_SITES=		http://rsmith.home.xs4all.nl/software/
PKGNAMEPREFIX=		${PYTHON_PKGNAMEPREFIX}

MAINTAINER=		rsmith@xs4all.nl
COMMENT=		Converts STL models to POV-Ray meshes or PostScript/PDF images

# bypass infrastructure bug
OPTIONSFILE=    ${PORT_DBDIR}/py27-${PORTNAME}/options

USE_ZIP=		YES
USE_PYTHON=		2.5+
USE_PYDISTUTILS=	YES

CONFLICTS=		stl2pov-[0-9]*

MAN1=			stl2ps.1 stlinfo.1

OPTIONS_DEFINE=	PYCAIRO
PYCAIRO_DESC=	Use (py)Cairo to enable stl2pdf

.include <bsd.port.options.mk>

.if ${PORT_OPTIONS:MPYCAIRO}
RUN_DEPENDS+=		${PYTHON_PKGNAMEPREFIX}cairo>1.8:${PORTSDIR}/graphics/py-cairo
MAN1+=			stl2pdf.1
PLIST_SUB+=		STL2PDF=""
.else
PLIST_SUB+=		STL2PDF="@comment "
.endif

NO_BUILD=		YES

post-install:
.if ${PORT_OPTIONS:MPYCAIRO}
	@${INSTALL_MAN} ${WRKSRC}/stl2pdf.1 ${MANPREFIX}/man/man1
	@${MV} ${PREFIX}/bin/stl2pdf.py ${PREFIX}/bin/stl2pdf
.else
	@${RM} -f ${PREFIX}/bin/stl2pdf.py
	@${RM} -f  ${MANPREFIX}/man/man1/stl2pdf.1*
.endif
	@${INSTALL_MAN} ${WRKSRC}/stl2ps.1 ${MANPREFIX}/man/man1
	@${INSTALL_MAN} ${WRKSRC}/stlinfo.1 ${MANPREFIX}/man/man1
	@${MV} ${PREFIX}/bin/stl2ps.py  ${PREFIX}/bin/stl2ps
	@${MV} ${PREFIX}/bin/stl2pov.py ${PREFIX}/bin/stl2pov
	@${MV} ${PREFIX}/bin/stlinfo.py ${PREFIX}/bin/stlinfo
	@${MV} ${PYTHON_SITELIBDIR}/py_stl-${PORTVERSION}-py${PYTHON_VER}.egg-info ${PYTHON_SITELIBDIR}/${PYDISTUTILS_EGGINFO}

.include <bsd.port.mk>
