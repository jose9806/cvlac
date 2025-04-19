CREATE TABLE "public"."identificacion"
(
 "cvlac_id"                 varchar NOT NULL,
 "categoria"                varchar NULL,
 "nombre_completo"          varchar NULL,
 "nombre_citaciones"        varchar NULL,
 "nacionalidad"             varchar NULL,
 "genero"                   varchar NULL,
 "codigo_orcid"             varchar NULL,
 "author_id_scopus"         varchar NULL,
 "reconocido_colciencias"   varchar NULL,
 CONSTRAINT "PK_identificacion" PRIMARY KEY ( "cvlac_id" )
);


CREATE TABLE "public"."formacion_academica"
(
 "id"                 bigserial,
 "cvlac_id"           varchar NOT NULL,
 "fecha_inicio"       varchar NULL,
 "fecha_fin"          varchar NULL,
 "nivel_formacion"    varchar NULL,
 "institucion"        varchar NULL,
 "programa_academico" varchar NULL,
 CONSTRAINT "cvlac_id" FOREIGN KEY ( "cvlac_id" ) REFERENCES "public"."identificacion" ( "cvlac_id" ) ON DELETE CASCADE,
 CONSTRAINT "PK_formacion_academica" PRIMARY KEY ( "id" )
);


CREATE TABLE "public"."formacion_complementaria"
(
 "id"                 bigserial,
 "cvlac_id"           varchar NOT NULL,
 "fecha_inicio"       varchar NULL,
 "fecha_fin"          varchar NULL,
 "nivel_formacion"    varchar NULL,
 "institucion"        varchar NULL,
 "programa_academico" varchar NULL,
 CONSTRAINT "cvlac_id" FOREIGN KEY ( "cvlac_id" ) REFERENCES "public"."identificacion" ( "cvlac_id" ) ON DELETE CASCADE,
 CONSTRAINT "PK_formacion_complementaria" PRIMARY KEY ( "id" )
);


CREATE TABLE "public"."experiencia"
(
 "id"                 bigserial,
 "cvlac_id"           varchar NOT NULL,
 "institucion"        varchar NULL,
 "ano_inicio"         int NULL,
 "ano_fin"            int NULL,
 "dedicacion"         varchar NULL,
 CONSTRAINT "cvlac_id" FOREIGN KEY ( "cvlac_id" ) REFERENCES "public"."identificacion" ( "cvlac_id" ) ON DELETE CASCADE,
 CONSTRAINT "PK_experiencia" PRIMARY KEY ( "id" )
);



CREATE TABLE "public"."lineas_investigacion"
(
 "id"                   bigserial,
 "cvlac_id"             varchar NOT NULL,
 "linea_investigacion"  varchar NULL,
 "activa"               varchar NULL,
 CONSTRAINT "cvlac_id" FOREIGN KEY ( "cvlac_id" ) REFERENCES "public"."identificacion" ( "cvlac_id" ) ON DELETE CASCADE,
 CONSTRAINT "PK_lineas_investigacion" PRIMARY KEY ( "id" )
);


CREATE TABLE "public"."areas_actuacion"
(
 "cvlac_id"     varchar NOT NULL,
 "gran_area"    varchar NULL,
 "area"         varchar NULL,
 "especialidad" varchar NULL,
 CONSTRAINT "cvlac_id" FOREIGN KEY ( "cvlac_id" ) REFERENCES "public"."identificacion" ( "cvlac_id" ) ON DELETE CASCADE,
 CONSTRAINT "PK_areas_actuacion" PRIMARY KEY ( "cvlac_id", "especialidad" )
);


CREATE TABLE "public"."idioma"
(
 "cvlac_id" varchar NOT NULL,
 "idioma"   varchar NULL,
 "habla"    varchar NULL,
 "lee"      varchar NULL,
 "escribe"  varchar NULL,
 "entiende" varchar NULL,
 CONSTRAINT "cvlac_id" FOREIGN KEY ( "cvlac_id" ) REFERENCES "public"."identificacion" ( "cvlac_id" ) ON DELETE CASCADE,
 CONSTRAINT "PK_idioma" PRIMARY KEY ( "cvlac_id", "idioma" )
);


CREATE TABLE "public"."cursos_corta_duracion"
(
 "id"                           bigserial,
 "cvlac_id"                     varchar NOT NULL,
 "chulo"                        varchar NULL,
 "coautores"                    varchar NULL,
 "nivel_programa_academico"     varchar NULL,
 "nombre_producto"              varchar NULL,
 "ano"                          int NULL,
 "pais"                         varchar NULL,
 "participacion"                varchar NULL,
 "duracion"                     varchar NULL,
 "finalidad"                    varchar NULL,
 "institucion_financiadora"     varchar NULL,
 "palabras"                     varchar NULL,
 "areas"                        varchar NULL,
 "sectores"                     varchar NULL,
 CONSTRAINT "cvlac_id" FOREIGN KEY ( "cvlac_id" ) REFERENCES "public"."identificacion" ( "cvlac_id" ) ON DELETE CASCADE,
 CONSTRAINT "PK_cursos_corta_duracion" PRIMARY KEY ( "id" )
);

CREATE TABLE "public"."trabajos_dirigidos"
(
 "id"                   bigserial,
 "cvlac_id"             varchar NOT NULL,
 "chulo"                varchar NULL,
 "coautores"            varchar NULL,
 "tipo_producto"        varchar NULL,
 "nombre"               varchar NULL,
 "fecha_inicio"         int NULL,
 "tipo_orientacion"     varchar NULL,
 "persona_orientada"    varchar NULL,
 "institucion"          varchar NULL,
 "programa_academico"   varchar NULL,
 "estado"               varchar NULL,
 "palabras"             varchar NULL,
 "areas"                varchar NULL,
 "sectores"             varchar NULL,
 CONSTRAINT "cvlac_id" FOREIGN KEY ( "cvlac_id" ) REFERENCES "public"."identificacion" ( "cvlac_id" ) ON DELETE CASCADE,
 CONSTRAINT "PK_trabajos_dirigidos_tutorias" PRIMARY KEY ( "id" )
);


CREATE TABLE "public"."asesorias"
(
 "id"                       bigserial,
 "cvlac_id"                 varchar NOT NULL,
 "chulo"                    varchar NULL,
 "nombre_proyecto_ondas"    varchar NULL,
 "institucion"              varchar NULL,
 "ciudad"                   varchar NULL,
 CONSTRAINT "cvlac_id" FOREIGN KEY ( "cvlac_id" ) REFERENCES "public"."identificacion" ( "cvlac_id" ) ON DELETE CASCADE,
 CONSTRAINT "PK_asesorias" PRIMARY KEY ( "id" )
);


CREATE TABLE "public"."jurados"
(
 "id"                       bigserial,
 "cvlac_id"                 varchar NOT NULL,
 "nivel_programa_academico" varchar  NULL,
 "chulo"                    varchar NULL,
 "coautores"                varchar NULL,         
 "titulo"                   varchar NULL,
 "tipo_trabajo"             varchar NULL,
 "institucion"              varchar NULL,           
 "programa_academico"       varchar NULL,
 "nombre_orientado"         varchar NULL,
 "palabras"                 varchar NULL,
 "areas"                    varchar NULL,
 "sectores"                 varchar NULL,
 CONSTRAINT "cvlac_id" FOREIGN KEY ( "cvlac_id" ) REFERENCES "public"."identificacion" ( "cvlac_id" ) ON DELETE CASCADE,
 CONSTRAINT "PK_jurados" PRIMARY KEY ( "id" )
);


CREATE TABLE "public"."par_evaluador"
(
 "id"                   bigserial,
 "cvlac_id"             varchar NULL,
 "ambito"               varchar  NULL,
 "par_evaluador_de"     varchar NULL,         
 "entidad_convocadora"  varchar NULL,
 "tipo_material"        varchar NULL,
 "ano"                  int NULL,           
 "mes"                  varchar NULL,
 CONSTRAINT "cvlac_id" FOREIGN KEY ( "cvlac_id" ) REFERENCES "public"."identificacion" ( "cvlac_id" ) ON DELETE CASCADE,
 CONSTRAINT "PK_par_evaluador" PRIMARY KEY ( "id" )
);


CREATE TABLE "public"."participacion_comites_evaluacion"
(
 "id"              bigserial,
 "cvlac_id"        varchar NOT NULL,
 "chulo"           varchar NULL,
 "tipo"            varchar NULL,
 "institucion"     varchar NULL,         
 "nombre_producto" varchar NULL,
 "ano"             int NULL,
 CONSTRAINT "cvlac_id" FOREIGN KEY ( "cvlac_id" ) REFERENCES "public"."identificacion" ( "cvlac_id" ) ON DELETE CASCADE,
 CONSTRAINT "PK_participacion_comites_evaluacion" PRIMARY KEY ( "id" )
);


CREATE TABLE "public"."consultorias"
(
 "id"               bigserial,
 "cvlac_id"         varchar NOT NULL,
 "chulo"            varchar NULL,
 "tipo_clase"       varchar NULL,
 "nombre"           varchar NULL,
 "numero_contrato"  varchar NULL,         
 "pais"             varchar NULL,
 "ano"              int NULL,
 "duracion"         varchar NULL,
 "palabras"         varchar NULL,
 "areas"            varchar NULL,
 "sectores"         varchar NULL,
 CONSTRAINT "cvlac_id" FOREIGN KEY ( "cvlac_id" ) REFERENCES "public"."identificacion" ( "cvlac_id" ) ON DELETE CASCADE,
 CONSTRAINT "PK_consultorias" PRIMARY KEY ( "id" )
);


CREATE TABLE "public"."ediciones_revisiones"
(
 "id"               bigserial,
 "cvlac_id"         varchar NOT NULL,
 "chulo"            varchar NULL,
 "tipo_producto"    varchar NULL,
 "pais"             varchar NULL,
 "ano"              int NULL,
 "editorial"        varchar NULL,
 "paginas"          int NULL,
 "revista"          varchar NULL,
 CONSTRAINT "cvlac_id" FOREIGN KEY ( "cvlac_id" ) REFERENCES "public"."identificacion" ( "cvlac_id" ) ON DELETE CASCADE,
 CONSTRAINT "PK_ediciones_revisiones" PRIMARY KEY ( "id" )
);


CREATE TABLE "public"."eventos_cientificos"
(
 "id"               varchar,
 "cvlac_id"         varchar NULL,
 "chulo"            varchar NULL,
 "nombre_evento"    varchar NULL,
 "tipo_evento"      varchar NULL,
 "ambito"           varchar NULL,
 "fecha_inicio"     varchar NULL,
 "fecha_fin"        varchar NULL,
 "ciudad"           varchar NULL,
 "lugar"            varchar NULL,
 "rol"              varchar NULL,
 CONSTRAINT "cvlac_id" FOREIGN KEY ( "cvlac_id" ) REFERENCES "public"."identificacion" ( "cvlac_id" ) ON DELETE CASCADE,
 CONSTRAINT "PK_eventos_cientificos" PRIMARY KEY ( "id" )
);


CREATE TABLE "public"."eventos_participantes"
(
 "id"        bigserial,
 "nombre"    varchar NULL,
 "rol"       varchar NULL,
 "evento_id" varchar,
 CONSTRAINT "evento_id" FOREIGN KEY ( "evento_id" ) REFERENCES "public"."eventos_cientificos" ( "id" ) ON DELETE CASCADE,
 CONSTRAINT "PK_eventos_participantes" PRIMARY KEY ( "id" )
);


CREATE TABLE "public"."eventos_productos"
(
 "id"               bigserial,
 "nombre"           varchar NULL,
 "tipo_producto"    varchar NULL,
 "evento_id"        varchar,
 CONSTRAINT "evento_id" FOREIGN KEY ( "evento_id" ) REFERENCES "public"."eventos_cientificos" ( "id" ) ON DELETE CASCADE,
 CONSTRAINT "PK_eventos_productos" PRIMARY KEY ( "id" )
);


CREATE TABLE "public"."eventos_instituciones"
(
 "id"               bigserial,
 "nombre"           varchar NULL,
 "tipo_vinculacion" varchar NULL,
 "evento_id"        varchar,
 CONSTRAINT "evento_id" FOREIGN KEY ( "evento_id" ) REFERENCES "public"."eventos_cientificos" ( "id" ) ON DELETE CASCADE,
 CONSTRAINT "PK_eventos_instituciones" PRIMARY KEY ( "id" )
);


CREATE TABLE "public"."informes_investigacion"
(
 "id"           bigserial,
 "cvlac_id"     varchar NULL,
 "titulo"       varchar NULL,
 "ano"          int NULL,
 "coautores"    varchar NULL,
 CONSTRAINT "cvlac_id" FOREIGN KEY ( "cvlac_id" ) REFERENCES "public"."identificacion" ( "cvlac_id" ) ON DELETE CASCADE,
 CONSTRAINT "PK_informes_investigacion" PRIMARY KEY ( "id" )
);


CREATE TABLE "public"."redes_conocimiento"
(
 "id"               bigserial,
 "cvlac_id"         varchar NULL,
 "nombre"           varchar NULL,
 "tipo"             varchar NULL,
 "fecha_inicio"     varchar NULL,
 "lugar"            varchar NULL,
 "participantes"    int NULL,
 CONSTRAINT "cvlac_id" FOREIGN KEY ( "cvlac_id" ) REFERENCES "public"."identificacion" ( "cvlac_id" ) ON DELETE CASCADE,
 CONSTRAINT "PK_redes_conocimiento" PRIMARY KEY ( "id" )
);


CREATE TABLE "public"."audio"
(
 "id"           bigserial,
 "cvlac_id"     varchar NULL,
 "titulo"       varchar NULL,
 "fecha"        varchar NULL,
 "lugar"        varchar NULL,
 "coautores"    varchar NULL,
 "formato"      varchar NULL,
 "descripcion"  varchar NULL,
 "palabras"     varchar NULL,
 "areas"        varchar NULL,
 "sectores"     varchar NULL,
 CONSTRAINT "cvlac_id" FOREIGN KEY ( "cvlac_id" ) REFERENCES "public"."identificacion" ( "cvlac_id" ) ON DELETE CASCADE,
 CONSTRAINT "PK_audio" PRIMARY KEY ( "id" )
);


CREATE TABLE "public"."impresa"
(
 "id"                   bigserial,
 "cvlac_id"             varchar NULL,
 "nombre"               varchar NULL,
 "tipo"                 varchar NULL,
 "chulo"                varchar NULL,
 "medio_circulacion"    varchar NULL,
 "sitio_web"            varchar NULL,
 "fecha"                varchar NULL,
 "ambito"               varchar NULL,
 CONSTRAINT "cvlac_id" FOREIGN KEY ( "cvlac_id" ) REFERENCES "public"."identificacion" ( "cvlac_id" ) ON DELETE CASCADE,
 CONSTRAINT "PK_impresa" PRIMARY KEY ( "id" )
);


CREATE TABLE "public"."multimedia"
(
 "id"         bigserial,
 "cvlac_id"   varchar NULL,
 "chulo"      varchar NULL,
 "nombre"     varchar NULL,
 "tipo"       varchar NULL,
 "ano"        int NULL,
 "pais"       varchar NULL,
 "duracion"   int NULL,
 "emisora"    varchar NULL,
 "coautores"  varchar NULL,
 "palabras"   varchar NULL,
 "areas"      varchar NULL,
 "sectores"   varchar NULL,
 CONSTRAINT "cvlac_id" FOREIGN KEY ( "cvlac_id" ) REFERENCES "public"."identificacion" ( "cvlac_id" ) ON DELETE CASCADE,
 CONSTRAINT "PK_multimedia" PRIMARY KEY ( "id" )
);


CREATE TABLE "public"."secuencias_geneticas"
(
 "id"               bigserial,
 "cvlac_id"         varchar NULL,
 "chulo"            varchar NULL,
 "nombre"           varchar NULL,
 "fecha"            varchar NULL,
 "ciudad"           varchar NULL,
 "base_datos"       varchar NULL,
 "disponible_en"    varchar NULL,
 "institucion"      varchar NULL,
 "coautores"        varchar NULL,
 "palabras"         varchar NULL,
 "areas"            varchar NULL,
 "sectores"         varchar NULL,
 CONSTRAINT "cvlac_id" FOREIGN KEY ( "cvlac_id" ) REFERENCES "public"."identificacion" ( "cvlac_id" ) ON DELETE CASCADE,
 CONSTRAINT "PK_secuencias_geneticas" PRIMARY KEY ( "id" )
);


CREATE TABLE "public"."contenido_virtual"
(
 "id"               bigserial,
 "cvlac_id"         varchar NULL,
 "titulo"           varchar NULL,
 "tipo"             varchar NULL,
 "fecha"            varchar NULL,
 "disponible_en"    varchar NULL,
 "descripcion"      varchar NULL,
 CONSTRAINT "cvlac_id" FOREIGN KEY ( "cvlac_id" ) REFERENCES "public"."identificacion" ( "cvlac_id" ) ON DELETE CASCADE,
 CONSTRAINT "PK_contenido_virtual" PRIMARY KEY ( "id" )
);


CREATE TABLE "public"."estrategias_comunicacion"
(
 "id"               bigserial,
 "cvlac_id"         varchar NULL,
 "nombre"           varchar NULL,
 "fecha_inicio"     varchar NULL,
 "fecha_fin"        varchar NULL,
 CONSTRAINT "cvlac_id" FOREIGN KEY ( "cvlac_id" ) REFERENCES "public"."identificacion" ( "cvlac_id" ) ON DELETE CASCADE,
 CONSTRAINT "PK_estrategias_comunicacion" PRIMARY KEY ( "id" )
);


CREATE TABLE "public"."estrategias_pedagogicas"
(
 "id"               bigserial,
 "cvlac_id"         varchar NULL,
 "nombre"           varchar NULL,
 "fecha_inicio"     varchar NULL,
 "fecha_fin"        varchar NULL,
 CONSTRAINT "cvlac_id" FOREIGN KEY ( "cvlac_id" ) REFERENCES "public"."identificacion" ( "cvlac_id" ) ON DELETE CASCADE,
 CONSTRAINT "PK_estrategias_pedagogicas" PRIMARY KEY ( "id" )
);


CREATE TABLE "public"."espacios_participacion"
(
 "id"               bigserial,
 "cvlac_id"         varchar NULL,
 "nombre"           varchar NULL,
 "fecha_inicio"     varchar NULL,
 "fecha_fin"        varchar NULL,
 "ciudad"           varchar NULL,
 "participantes"    int NULL,
 CONSTRAINT "cvlac_id" FOREIGN KEY ( "cvlac_id" ) REFERENCES "public"."identificacion" ( "cvlac_id" ) ON DELETE CASCADE,
 CONSTRAINT "PK_espacios_participacion" PRIMARY KEY ( "id" )
);


CREATE TABLE "public"."participacion_proyectos"
(
 "id"               bigserial,
 "cvlac_id"         varchar NULL,
 "nombre"           varchar NULL,
 "fecha_inicio"     varchar NULL,
 "fecha_fin"        varchar NULL,
 CONSTRAINT "cvlac_id" FOREIGN KEY ( "cvlac_id" ) REFERENCES "public"."identificacion" ( "cvlac_id" ) ON DELETE CASCADE,
 CONSTRAINT "PK_participacion_proyectos" PRIMARY KEY ( "id" )
);



CREATE TABLE "public"."obras_productos"
(
 "id"             bigserial,
 "cvlac_id"       varchar NULL,
 "chulo"          varchar NULL,
 "nombre"         varchar NULL,
 "disciplina"     varchar NULL,
 "fecha_creacion" varchar NULL,
 CONSTRAINT "cvlac_id" FOREIGN KEY ( "cvlac_id" ) REFERENCES "public"."identificacion" ( "cvlac_id" ) ON DELETE CASCADE,
 CONSTRAINT "PK_obras_productos" PRIMARY KEY ( "id" )
);


CREATE TABLE "public"."registro_licencia"
(
 "id"                  bigserial,
 "cvlac_id"            varchar NULL,
 "chulo"               varchar NULL,
 "institucion"         varchar NULL,
 "fecha_otorgamiento"  varchar NULL,
 "numero_registro"     varchar NULL,
 "nacional_derechos"   varchar NULL,
 CONSTRAINT "cvlac_id" FOREIGN KEY ( "cvlac_id" ) REFERENCES "public"."identificacion" ( "cvlac_id" ) ON DELETE CASCADE,
 CONSTRAINT "PK_registro_licencia" PRIMARY KEY ( "id" )
);


CREATE TABLE "public"."industrias_creativas_culturales"
(
 "id"               bigserial,
 "cvlac_id"         varchar NULL,
 "nombre"           varchar NULL,
 "nit_registro"     varchar NULL,
 "fecha_registro"   varchar NULL,
 "tiene_productos"  varchar NULL,
 CONSTRAINT "cvlac_id" FOREIGN KEY ( "cvlac_id" ) REFERENCES "public"."identificacion" ( "cvlac_id" ) ON DELETE CASCADE,
 CONSTRAINT "PK_empresas_creativas" PRIMARY KEY ( "id" )
);


CREATE TABLE "public"."eventos_artisticos"
(
 "id"             bigserial,
 "cvlac_id"       varchar NULL,
 "chulo"          varchar NULL,
 "nombre"         varchar NULL,
 "fecha_inicio"   varchar NULL,
 CONSTRAINT "cvlac_id" FOREIGN KEY ( "cvlac_id" ) REFERENCES "public"."identificacion" ( "cvlac_id" ) ON DELETE CASCADE,
 CONSTRAINT "PK_eventos_artisticos" PRIMARY KEY ( "id" )
);


CREATE TABLE "public"."talleres_creativos"
(
 "id"                   bigserial,
 "cvlac_id"             varchar NULL,
 "chulo"                varchar NULL,
 "nombre"               varchar NULL,
 "tipo"                 varchar NULL,
 "fecha_inicio"         varchar NULL,
 "fecha_fin"            varchar NULL,
 "participacion"        varchar NULL,
 "ambito"               varchar NULL,
 "distincion_obtenida"  varchar NULL,
 "mecanismo_seleccion"  varchar NULL,
 "lugar_realizacion"    varchar NULL,
 CONSTRAINT "cvlac_id" FOREIGN KEY ( "cvlac_id" ) REFERENCES "public"."identificacion" ( "cvlac_id" ) ON DELETE CASCADE,
 CONSTRAINT "PK_talleres_creativos" PRIMARY KEY ( "id" )
);


CREATE TABLE "public"."articulos"
(
 "id"                  bigserial,
 "cvlac_id"            varchar NOT NULL,
 "chulo"               varchar NULL,
 "tipo"                varchar NULL,
 "coautores"           varchar NULL,
 "titulo"              varchar NULL,
 "pais"                varchar NULL,
 "revista"             varchar NULL,
 "issn"                varchar NULL,
 "editorial"           varchar NULL,
 "volumen"             varchar NULL,
 "fasciculo"           varchar NULL,
 "pagina_inicial"      int NULL,
 "pagina_final"        int NULL,
 "ano"                 int NULL,
 "doi"                 varchar NULL,
 "palabras"            varchar NULL,
 "areas"               varchar NULL,
 "sectores"            varchar NULL,
 CONSTRAINT "cvlac_id" FOREIGN KEY ( "cvlac_id" ) REFERENCES "public"."identificacion" ( "cvlac_id" ) ON DELETE CASCADE,
 CONSTRAINT "PK_articulos" PRIMARY KEY ( "id" )
);


CREATE TABLE "public"."capitulos_libro"
(
 "id"                  bigserial,
 "cvlac_id"            varchar NOT NULL,
 "tipo"                varchar NULL,
 "chulo"               varchar NULL,
 "coautores"           varchar NULL,
 "titulo_capitulo"     varchar NULL,
 "lugar_publicacion"   varchar NULL,
 "libro"               varchar NULL,
 "isbn"                varchar NULL,
 "editorial"           varchar NULL,
 "volumen"             varchar NULL,
 "pagina_inicial"      int NULL,
 "pagina_final"        int NULL,
 "ano"                 int NULL,
 "palabras"            varchar NULL,
 "areas"               varchar NULL,
 "sectores"            varchar NULL,
 CONSTRAINT "cvlac_id" FOREIGN KEY ( "cvlac_id" ) REFERENCES "public"."identificacion" ( "cvlac_id" ) ON DELETE CASCADE,
 CONSTRAINT "PK_capitulos_libro" PRIMARY KEY ( "id" )
);


CREATE TABLE "public"."libros"
(
 "id"                  bigserial,
 "cvlac_id"            varchar NOT NULL,
 "chulo"               varchar NULL,
 "tipo"                varchar NULL,
 "coautores"           varchar NULL,
 "titulo"              varchar NULL,
 "lugar_publicacion"   varchar NULL,
 "ano"                 int NULL,
 "editorial"           varchar NULL,
 "isbn"                varchar NULL,
 "volumen"             varchar NULL,
 "paginas"             varchar NULL,
 "palabras"            varchar NULL,
 "areas"               varchar NULL,
 "sectores"            varchar NULL,
 CONSTRAINT "cvlac_id" FOREIGN KEY ( "cvlac_id" ) REFERENCES "public"."identificacion" ( "cvlac_id" ) ON DELETE CASCADE,
 CONSTRAINT "PK_libros" PRIMARY KEY ( "id" )
);


CREATE TABLE "public"."documentos_trabajo"
(
 "id"         bigserial,
 "cvlac_id"   varchar NOT NULL,
 "nombre"     varchar NULL,
 "ano"        int NULL,
 "paginas"    varchar NULL,
 CONSTRAINT "cvlac_id" FOREIGN KEY ( "cvlac_id" ) REFERENCES "public"."identificacion" ( "cvlac_id" ) ON DELETE CASCADE,
 CONSTRAINT "PK_documentos_trabajo" PRIMARY KEY ( "id" )
);


CREATE TABLE "public"."otra_produccion"
(
 "id"         bigserial,
 "cvlac_id"   varchar NOT NULL,
 "chulo"      varchar NULL,
 "tipo"       varchar NULL,
 "coautores"  varchar NULL,
 "titulo"     varchar NULL,
 "ano"        int NULL,
 "palabras"   varchar NULL,
 "areas"      varchar NULL,
 "sectores"   varchar NULL,
 CONSTRAINT "cvlac_id" FOREIGN KEY ( "cvlac_id" ) REFERENCES "public"."identificacion" ( "cvlac_id" ) ON DELETE CASCADE,
 CONSTRAINT "PK_otra_produccion" PRIMARY KEY ( "id" )
);


CREATE TABLE "public"."textos_no_cientificas"
(
 "id"               bigserial,
 "cvlac_id"         varchar NOT NULL,
 "chulo"            varchar NULL,
 "tipo"             varchar NULL,
 "coautores"        varchar NULL,
 "titulo"           varchar NULL,
 "pais"             varchar NULL,
 "ano"              int NULL,
 "revista"          varchar NULL,
 "issn"             varchar NULL,
 "pagina_inicial"   int NULL,
 "pagina_final"     int NULL,
 "volumen"          varchar,
 "palabras"         varchar NULL,
 "areas"            varchar NULL,
 "sectores"         varchar NULL,
 CONSTRAINT "cvlac_id" FOREIGN KEY ( "cvlac_id" ) REFERENCES "public"."identificacion" ( "cvlac_id" ) ON DELETE CASCADE,
 CONSTRAINT "PK_textos_no_cientificas" PRIMARY KEY ( "id" )
);


CREATE TABLE "public"."traducciones"
(
 "id"                   bigserial,
 "cvlac_id"             varchar NOT NULL,
 "chulo"                varchar NULL,
 "tipo"                 varchar NULL,
 "coautores"            varchar NULL,
 "nombre"               varchar NULL,
 "pais"                 varchar NULL,
 "ano"                  int NULL,
 "idioma_original"      varchar NULL,
 "idioma_traduccion"    varchar NULL,
 "autor"                varchar NULL,
 "volumen"              varchar,
 "palabras"             varchar NULL,
 "areas"                varchar NULL,
 "sectores"             varchar NULL,
 CONSTRAINT "cvlac_id" FOREIGN KEY ( "cvlac_id" ) REFERENCES "public"."identificacion" ( "cvlac_id" ) ON DELETE CASCADE,
 CONSTRAINT "PK_traducciones" PRIMARY KEY ( "id" )
);


CREATE TABLE "public"."notas_cientificas"
(
 "id"                   bigserial,
 "cvlac_id"             varchar NOT NULL,
 "chulo"                varchar NULL,
 "coautores"            varchar NULL,
 "titulo_nota"          varchar NULL,
 "revista"              varchar NULL,
 "medio_divulgacion"    varchar NULL,
 "idioma_original"      varchar NULL,
 "issn"                 varchar NULL,
 "editorial"            varchar NULL,
 "volumen"              varchar,
 "fasc"                 varchar NULL,
 "pagina_inicial"       int NULL,
 "pagina_final"         int NULL,
 "ano"                  int NULL,
 "sitio_web"            varchar NULL,
 "doi"                  varchar NULL,
 "palabras"             varchar NULL,
 "areas"                varchar NULL,
 "sectores"             varchar NULL,
 CONSTRAINT "cvlac_id" FOREIGN KEY ( "cvlac_id" ) REFERENCES "public"."identificacion" ( "cvlac_id" ) ON DELETE CASCADE,
 CONSTRAINT "PK_notas_cientificas" PRIMARY KEY ( "id" )
);


CREATE TABLE "public"."cartas_mapas"
(
 "id"                   bigserial,
 "cvlac_id"             varchar NOT NULL,
 "chulo"                varchar NULL,
 "tipo"                 varchar NULL,
 "coautores"            varchar NULL,
 "nombre_producto"      varchar NULL,
 "pais"                 varchar NULL,
 "ano"                  int NULL,
 "palabras"             varchar NULL,
 "areas"                varchar NULL,
 "sectores"             varchar NULL,
 CONSTRAINT "cvlac_id" FOREIGN KEY ( "cvlac_id" ) REFERENCES "public"."identificacion" ( "cvlac_id" ) ON DELETE CASCADE,
 CONSTRAINT "PK_cartas_mapas" PRIMARY KEY ( "id" )
);


CREATE TABLE "public"."conceptos_tecnicos"
(
 "id"                    bigserial,
 "cvlac_id"              varchar NOT NULL,
 "titulo"                varchar NULL,
 "institucion"           varchar NULL,
 "ciudad"                varchar NULL,
 "fecha_solicitud"       varchar NULL,
 "fecha_envio"           varchar NULL,
 "numero"                varchar NULL,
 CONSTRAINT "cvlac_id" FOREIGN KEY ( "cvlac_id" ) REFERENCES "public"."identificacion" ( "cvlac_id" ) ON DELETE CASCADE,
 CONSTRAINT "PK_conceptos_tecnicos" PRIMARY KEY ( "id" )
);


CREATE TABLE "public"."diseno_industrial"
(
 "id"           bigserial,
 "cvlac_id"     varchar NOT NULL,
 "coautores"    varchar NULL,
 "nombre"       varchar NULL,
 "pais"         varchar NULL,
 "ano"          int NULL,
 "palabras"     varchar NULL,
 "areas"        varchar NULL,
 "sectores"     varchar NULL,
 CONSTRAINT "cvlac_id" FOREIGN KEY ( "cvlac_id" ) REFERENCES "public"."identificacion" ( "cvlac_id" ) ON DELETE CASCADE,
 CONSTRAINT "PK_diseno_industrial" PRIMARY KEY ( "id" )
);

CREATE TABLE "public"."empresas_base_tecnologica"
(
 "id"               bigserial,
 "cvlac_id"         varchar NOT NULL,
 "tipo"             varchar NULL,
 "chulo"            varchar NULL,
 "coautores"        varchar NULL,
 "nombre"           varchar NULL,
 "nit"              varchar NULL,
 "fecha_registro"   varchar NULL,
 "palabras"         varchar NULL,
 "areas"            varchar NULL,
 "sectores"         varchar NULL,
 CONSTRAINT "cvlac_id" FOREIGN KEY ( "cvlac_id" ) REFERENCES "public"."identificacion" ( "cvlac_id" ) ON DELETE CASCADE,
 CONSTRAINT "PK_empresas_base_tecnologica" PRIMARY KEY ( "id" )
);


CREATE TABLE "public"."esquemas_trazado"
(
 "id"           bigserial,
 "cvlac_id"     varchar NOT NULL,
 "coautores"    varchar NULL,
 "nombre"       varchar NULL,
 "pais"         varchar NULL,
 "ano"          int NULL,
 "palabras"     varchar NULL,
 "areas"        varchar NULL,
 "sectores"     varchar NULL,
 CONSTRAINT "cvlac_id" FOREIGN KEY ( "cvlac_id" ) REFERENCES "public"."identificacion" ( "cvlac_id" ) ON DELETE CASCADE,
 CONSTRAINT "PK_esquemas_trazado" PRIMARY KEY ( "id" )
);


CREATE TABLE "public"."informes_tecnicos"
(
 "id"                   bigserial,
 "cvlac_id"             varchar NOT NULL,
 "chulo"                varchar NULL,
 "coautores"            varchar NULL,
 "nombre"               varchar NULL,
 "contrato_registro"    varchar NULL,         
 "pais"                 varchar NULL,
 "ano"                  int NULL,
 "palabras"             varchar NULL,
 "areas"                varchar NULL,
 "sectores"             varchar NULL,
 CONSTRAINT "cvlac_id" FOREIGN KEY ( "cvlac_id" ) REFERENCES "public"."identificacion" ( "cvlac_id" ) ON DELETE CASCADE,
 CONSTRAINT "PK_informes_tecnicos" PRIMARY KEY ( "id" )
);


CREATE TABLE "public"."innovacion_procesos"
(
 "id"           bigserial,
 "cvlac_id"     varchar NOT NULL,
 "chulo"        varchar NULL,
 "coautores"    varchar NULL,
 "nombre"       varchar NULL,
 "pais"         varchar NULL,
 "ano"          int NULL,
 "palabras"     varchar NULL,
 "areas"        varchar NULL,
 "sectores"     varchar NULL,
 CONSTRAINT "cvlac_id" FOREIGN KEY ( "cvlac_id" ) REFERENCES "public"."identificacion" ( "cvlac_id" ) ON DELETE CASCADE,
 CONSTRAINT "PK_innovacion_procesos" PRIMARY KEY ( "id" )
);


CREATE TABLE "public"."innovacion_gestion"
(
 "id"           bigserial,
 "cvlac_id"     varchar NOT NULL,
 "tipo"                 varchar NULL,
 "coautores"    varchar NULL,
 "nombre"       varchar NULL,
 "pais"         varchar NULL,
 "ano"          int NULL,
 "palabras"     varchar NULL,
 "areas"        varchar NULL,
 "sectores"     varchar NULL,
 CONSTRAINT "cvlac_id" FOREIGN KEY ( "cvlac_id" ) REFERENCES "public"."identificacion" ( "cvlac_id" ) ON DELETE CASCADE,
 CONSTRAINT "PK_innovacion_gestion" PRIMARY KEY ( "id" )
);


CREATE TABLE "public"."variedad_animal"
(
 "id"           bigserial,
 "cvlac_id"     varchar NOT NULL,
 "chulo"        varchar NULL,
 "coautores"    varchar NULL,
 "nombre"       varchar NULL,
 "pais"         varchar NULL,
 "ano"          int NULL,
 "palabras"     varchar NULL,
 "areas"        varchar NULL,
 "sectores"     varchar NULL,
 CONSTRAINT "cvlac_id" FOREIGN KEY ( "cvlac_id" ) REFERENCES "public"."identificacion" ( "cvlac_id" ) ON DELETE CASCADE,
 CONSTRAINT "PK_variedad_animal" PRIMARY KEY ( "id" )
);


CREATE TABLE "public"."poblaciones_mejoradas"
(
 "id"                   bigserial,
 "cvlac_id"             varchar NOT NULL,
 "coautores"            varchar NULL,
 "nombre"               varchar NULL,
 "pais"                 varchar NULL,
 "ano"                  int NULL,
 "numero_certificado"   varchar,
 CONSTRAINT "cvlac_id" FOREIGN KEY ( "cvlac_id" ) REFERENCES "public"."identificacion" ( "cvlac_id" ) ON DELETE CASCADE,
 CONSTRAINT "PK_poblaciones_mejoradas" PRIMARY KEY ( "id" )
);


CREATE TABLE "public"."variedad_vegetal"
(
 "id"           bigserial,
 "cvlac_id"     varchar NOT NULL,
 "chulo"        varchar NULL,
 "coautores"    varchar NULL,
 "nombre"       varchar NULL,
 "ciclo"        varchar NULL,
 "estado"       varchar NULL,
 "pais"         varchar NULL,
 "ano"          int NULL,
 "palabras"     varchar NULL,
 "areas"        varchar NULL,
 "sectores"     varchar NULL,
 CONSTRAINT "cvlac_id" FOREIGN KEY ( "cvlac_id" ) REFERENCES "public"."identificacion" ( "cvlac_id" ) ON DELETE CASCADE,
 CONSTRAINT "PK_variedad_vegetal" PRIMARY KEY ( "id" )
);


CREATE TABLE "public"."registro_cientifico"
(
 "id"                           bigserial,
 "cvlac_id"                     varchar NOT NULL,
 "chulo"                        varchar NULL,
 "coautores"                    varchar NULL,
 "nombre"                       varchar NULL,
 "ano"                          int NULL,
 "pais"                         varchar NULL,
 "base_datos"                   varchar NULL,
 "sitio_web"                    varchar NULL,
 "institucion_registro"         varchar NULL,
 "institucion_certificadora"    varchar NULL,
 "articulo_vinculado"           varchar NULL,
 "palabras"                     varchar NULL,
 "areas"                        varchar NULL,
 "sectores"                     varchar NULL,
 CONSTRAINT "cvlac_id" FOREIGN KEY ( "cvlac_id" ) REFERENCES "public"."identificacion" ( "cvlac_id" ) ON DELETE CASCADE,
 CONSTRAINT "PK_registro_cientifico" PRIMARY KEY ( "id" )
);


CREATE TABLE "public"."plantas_piloto"
(
 "id"                 bigserial,
 "cvlac_id"           varchar NOT NULL,
 "chulo"              varchar NULL,
 "coautores"          varchar NULL,
 "nombre"             varchar NULL,
 "nombre_comercial"   varchar NULL,
 "pais"               varchar NULL,
 "ano"                int NULL,
 "palabras"           varchar NULL,
 "areas"              varchar NULL,
 "sectores"           varchar NULL,
 CONSTRAINT "cvlac_id" FOREIGN KEY ( "cvlac_id" ) REFERENCES "public"."identificacion" ( "cvlac_id" ) ON DELETE CASCADE,
 CONSTRAINT "PK_plantas_piloto" PRIMARY KEY ( "id" )
);


CREATE TABLE "public"."productos_nutraceuticos"
(
 "id"                   bigserial,
 "cvlac_id"             varchar NOT NULL,
 "chulo"                varchar NULL,
 "coautores"            varchar NULL,
 "nombre"               varchar NULL,
 "fecha_registro"       varchar NULL,
 "pais"                 varchar NULL,
 "titular"              varchar NULL,
 "numero_registro"      varchar,
 "numero_contrato"      varchar NULL,         
 "proyecto_vinculado"   varchar NULL,

 CONSTRAINT "cvlac_id" FOREIGN KEY ( "cvlac_id" ) REFERENCES "public"."identificacion" ( "cvlac_id" ) ON DELETE CASCADE,
 CONSTRAINT "PK_productos_nutraceuticos" PRIMARY KEY ( "id" )
);


CREATE TABLE "public"."productos_tecnologicos"
(
 "id"                 bigserial,
 "cvlac_id"           varchar NOT NULL,
 "tipo"               varchar NULL,
 "coautores"          varchar NULL,
 "nombre"             varchar NULL,
 "nombre_comercial"   varchar NULL,
 "pais"               varchar NULL,
 "ano"                int NULL,
 "palabras"           varchar NULL,
 "areas"              varchar NULL,
 "sectores"           varchar NULL,
 CONSTRAINT "cvlac_id" FOREIGN KEY ( "cvlac_id" ) REFERENCES "public"."identificacion" ( "cvlac_id" ) ON DELETE CASCADE,
 CONSTRAINT "PK_productos_tecnologicos" PRIMARY KEY ( "id" )
);


CREATE TABLE "public"."prototipos"
(
 "id"                 bigserial,
 "cvlac_id"           varchar NOT NULL,
 "chulo"              varchar NULL,
 "tipo"               varchar NULL,
 "coautores"          varchar NULL,
 "nombre"             varchar NULL,
 "nombre_comercial"   varchar NULL,
 "pais"               varchar NULL,
 "ano"                int NULL,
 "palabras"           varchar NULL,
 "areas"              varchar NULL,
 "sectores"           varchar NULL,
 CONSTRAINT "cvlac_id" FOREIGN KEY ( "cvlac_id" ) REFERENCES "public"."identificacion" ( "cvlac_id" ) ON DELETE CASCADE,
 CONSTRAINT "PK_prototipos" PRIMARY KEY ( "id" )
);


CREATE TABLE "public"."normas_regulaciones"
(
 "id"                 bigserial,
 "cvlac_id"           varchar NOT NULL,
 "chulo"              varchar NULL,
 "tipo"               varchar NULL,
 "coautores"          varchar NULL,
 "nombre"             varchar NULL,
 "nombre_comercial"   varchar NULL,
 "pais"               varchar NULL,
 "ano"                int NULL,
 "palabras"           varchar NULL,
 "areas"              varchar NULL,
 "sectores"           varchar NULL,
 CONSTRAINT "cvlac_id" FOREIGN KEY ( "cvlac_id" ) REFERENCES "public"."identificacion" ( "cvlac_id" ) ON DELETE CASCADE,
 CONSTRAINT "PK_normas_regulaciones" PRIMARY KEY ( "id" )
);


CREATE TABLE "public"."protocolos_vigilancia"
(
 "id"                 bigserial,
 "cvlac_id"           varchar NOT NULL,
 "chulo"              varchar NULL,
 "coautores"          varchar NULL,
 "nombre"             varchar NULL,
 "fecha"              varchar NULL,
 "ciudad"             varchar NULL,
 "institucion"        varchar NULL,
 "palabras"           varchar NULL,
 "areas"              varchar NULL,
 "sectores"           varchar NULL,
 CONSTRAINT "cvlac_id" FOREIGN KEY ( "cvlac_id" ) REFERENCES "public"."identificacion" ( "cvlac_id" ) ON DELETE CASCADE,
 CONSTRAINT "PK_protocolos_vigilancia" PRIMARY KEY ( "id" )
);


CREATE TABLE "public"."reglamentos"
(
 "id"                 bigserial,
 "cvlac_id"           varchar NOT NULL,
 "chulo"              varchar NULL,
 "coautores"          varchar NULL,
 "nombre"             varchar NULL,
 "nombre_comercial"   varchar NULL,
 "pais"               varchar NULL,
 "ano"                int NULL,
 "palabras"           varchar NULL,
 "areas"              varchar NULL,
 "sectores"           varchar NULL,
 CONSTRAINT "cvlac_id" FOREIGN KEY ( "cvlac_id" ) REFERENCES "public"."identificacion" ( "cvlac_id" ) ON DELETE CASCADE,
 CONSTRAINT "PK_reglamentos" PRIMARY KEY ( "id" )
);


CREATE TABLE "public"."signos_distintivos"
(
 "id"                 bigserial,
 "cvlac_id"           varchar NOT NULL,
 "chulo"              varchar NULL,
 "tipo"               varchar NULL,
 "nombre"             varchar NULL,
 "pais"               varchar NULL,
 "ano"                int NULL,
 "registro"           varchar NULL,
 "titular"           varchar NULL,
 CONSTRAINT "cvlac_id" FOREIGN KEY ( "cvlac_id" ) REFERENCES "public"."identificacion" ( "cvlac_id" ) ON DELETE CASCADE,
 CONSTRAINT "PK_signos_distintivos" PRIMARY KEY ( "id" )
);


CREATE TABLE "public"."software"
(
 "id"                 bigserial,
 "cvlac_id"           varchar NOT NULL,
 "tipo"               varchar NULL,
 "coautores"          varchar NULL,
 "nombre"             varchar NULL,
 "nombre_comercial"   varchar NULL,
 "contrato_registro"  varchar NULL,         
 "pais"               varchar NULL,
 "ano"                int NULL,
 "plataforma"         varchar NOT NULL,
 "ambiente"           varchar NOT NULL,
 "palabras"           varchar NULL,
 "areas"              varchar NULL,
 "sectores"           varchar NULL,
 CONSTRAINT "cvlac_id" FOREIGN KEY ( "cvlac_id" ) REFERENCES "public"."identificacion" ( "cvlac_id" ) ON DELETE CASCADE,
 CONSTRAINT "PK_software" PRIMARY KEY ( "id" )
);


CREATE TABLE "public"."demas_trabajos"
(
 "id"           bigserial,
 "cvlac_id"     varchar NOT NULL,
 "coautores"    varchar NULL,
 "nombre"       varchar NULL,
 "pais"         varchar NULL,
 "ano"          int NULL,
 "finalidad"    varchar NULL,
 "palabras"     varchar NULL,
 "areas"        varchar NULL,
 "sectores"     varchar NULL,
 CONSTRAINT "cvlac_id" FOREIGN KEY ( "cvlac_id" ) REFERENCES "public"."identificacion" ( "cvlac_id" ) ON DELETE CASCADE,
 CONSTRAINT "PK_demas_trabajos" PRIMARY KEY ( "id" )
);


CREATE TABLE "public"."proyectos"
(
 "id"           bigserial,
 "cvlac_id"     varchar NOT NULL,
 "chulo"        varchar NULL,
 "tipo"         varchar NULL,
 "nombre"       varchar NULL,
 "fecha_inicio" varchar NULL,
 "fecha_fin"    varchar NULL,
 "duracion"     varchar NULL,
 "resumen"      varchar NULL,
 CONSTRAINT "cvlac_id" FOREIGN KEY ( "cvlac_id" ) REFERENCES "public"."identificacion" ( "cvlac_id" ) ON DELETE CASCADE,
 CONSTRAINT "PK_proyectos" PRIMARY KEY ( "id" )
);


CREATE TABLE "public"."reconocimientos"
(
 "id"           bigserial,
 "cvlac_id"     varchar NOT NULL,
 "nombre"       varchar NULL,
 "fecha"        varchar NULL,
"institucion"   varchar NULL,
 CONSTRAINT "cvlac_id" FOREIGN KEY ( "cvlac_id" ) REFERENCES "public"."identificacion" ( "cvlac_id" ) ON DELETE CASCADE,
 CONSTRAINT "PK_reconocimientos" PRIMARY KEY ( "id" )
);


CREATE TABLE "public"."redes_sociales"
(
 "id"                 bigserial,
 "cvlac_id"           varchar NOT NULL,
 "red"                varchar NULL,
 "link"               varchar NULL,
 CONSTRAINT "cvlac_id" FOREIGN KEY ( "cvlac_id" ) REFERENCES "public"."identificacion" ( "cvlac_id" ) ON DELETE CASCADE,
 CONSTRAINT "PK_redes_sociales" PRIMARY KEY ( "id" )
);