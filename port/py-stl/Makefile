# New ports collection makefile for:    py-stl
# Date created:                         28 Dec 2011
# Whom:                                 rsmith@xs4all.nl
#
# $FreeBSD$

PORTNAME=		py-stl
PORTVERSION=		3.1
CATEGORIES=		graphics
MASTER_SITES=		http://rsmith.home.xs4all.nl/software/
PKGNAMEPREFIX=		${PYTHON_PKGNAMEPREFIX}

MAINTAINER=		rsmith@xs4all.nl
COMMENT=		Converts STL models to POV-Ray meshes or PostScript/PDF images

OPTIONS_DEFINE=		STL2PDF
STL2PDF_DESC=		"Add support for generating PDF images (requires Cairo)"
OPTIONS_DEFAULT=	STL2PDF

USE_ZIP=		YES
USE_PYTHON=		2.5+
USE_PYDISTUTILS=	YES

CONFLICTS=		stl2pov-[0-9]*

MAN1=			stl2ps.1 stlinfo.1

.if ${PORT_OPTIONS:MSTL2PDF}
RUN_DEPENDS+=		${PYTHON_PKGNAMEPREFIX}cairo>1.8:${PORTSDIR}/print/py-cairo
MAN1+=			stl2pdf.1
PLIST_SUB+=		STL2PDF=""
.else
PLIST_SUB+=		STL2PDF="@comment "
.endif

NO_BUILD=		YES

.include <bsd.port.pre.mk>

post-install:
.if ${PORT_OPTIONS:MSTL2PDF}
	@${INSTALL_MAN} ${WRKSRC}/stl2pdf.1 ${MANPREFIX}/man/man1
	@${MV} ${PREFIX}/bin/stl2pdf.py ${PREFIX}/bin/stl2pdf
.else
	@${RM} ${PREFIX}/bin/stl2pdf.py
.endif
	@${INSTALL_MAN} ${WRKSRC}/stl2ps.1 ${MANPREFIX}/man/man1
	@${INSTALL_MAN} ${WRKSRC}/stlinfo.1 ${MANPREFIX}/man/man1
	@${MV} ${PREFIX}/bin/stl2ps.py  ${PREFIX}/bin/stl2ps
	@${MV} ${PREFIX}/bin/stl2pov.py ${PREFIX}/bin/stl2pov
	@${MV} ${PREFIX}/bin/stlinfo.py ${PREFIX}/bin/stlinfo
	@${MV} ${PYTHON_SITELIBDIR}/py_stl-${PORTVERSION}-py${PYTHON_VER}.egg-info ${PYTHON_SITELIBDIR}/${PYDISTUTILS_EGGINFO}

.include <bsd.port.post.mk>
