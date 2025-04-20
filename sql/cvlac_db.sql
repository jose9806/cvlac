-- Schema completo para la base de datos CvLAC
-- Creado para resolver problemas con los extractores de datos

-- Configuración para reducir mensajes de error
SET client_min_messages TO WARNING;

-- Desactivar verificación de restricciones temporalmente para facilitar la eliminación de tablas
SET session_replication_role = 'replica';

-- Eliminar todas las tablas existentes en orden inverso de dependencias si existen
DO $$ 
DECLARE
    tables TEXT[] := ARRAY[
        'investigador_grupo', 'articulos_publicados', 'eventos_productos', 'eventos_participantes', 
        'eventos_instituciones', 'eventos_cientificos', 'eventos_artisticos', 'redes_conocimiento',
        'reconocimientos', 'lineas_investigacion', 'idioma', 'areas_actuacion', 'experiencia',
        'formacion_complementaria', 'formacion_academica', 'software', 'libros', 'capitulos_libro',
        'articulos', 'proyectos', 'identificacion', 'cursos_corta_duracion', 'trabajos_dirigidos',
        'asesorias', 'jurados', 'par_evaluador', 'participacion_comites_evaluacion', 'consultorias',
        'ediciones_revisiones', 'informes_investigacion', 'audio', 'impresa', 'multimedia',
        'secuencias_geneticas', 'contenido_virtual', 'estrategias_comunicacion',
        'estrategias_pedagogicas', 'espacios_participacion', 'participacion_proyectos',
        'obras_productos', 'registro_licencia', 'industrias_creativas_culturales', 'talleres_creativos',
        'documentos_trabajo', 'otra_produccion', 'textos_no_cientificas', 'traducciones',
        'notas_cientificas', 'cartas_mapas', 'conceptos_tecnicos', 'diseno_industrial',
        'empresas_base_tecnologica', 'esquemas_trazado', 'informes_tecnicos', 'innovacion_procesos',
        'innovacion_gestion', 'variedad_animal', 'poblaciones_mejoradas', 'variedad_vegetal',
        'registro_cientifico', 'plantas_piloto', 'productos_nutraceuticos', 'productos_tecnologicos',
        'prototipos', 'normas_regulaciones', 'protocolos_vigilancia', 'reglamentos',
        'signos_distintivos', 'demas_trabajos', 'redes_sociales'
    ];
    tbl TEXT;
BEGIN
    FOREACH tbl IN ARRAY tables LOOP
        EXECUTE format('DROP TABLE IF EXISTS %I CASCADE', tbl);
    END LOOP;
END $$;

-- Restaurar verificación de restricciones
SET session_replication_role = 'origin';

-- Crear tabla identificacion
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
 CONSTRAINT "PK_identificacion" PRIMARY KEY ("cvlac_id")
);

-- Crear tabla formacion_academica
CREATE TABLE "public"."formacion_academica"
(
 "id"                 bigserial,
 "cvlac_id"           varchar NOT NULL,
 "fecha_inicio"       varchar NULL,
 "fecha_fin"          varchar NULL,
 "nivel_formacion"    varchar NULL,
 "institucion"        varchar NULL,
 "programa_academico" varchar NULL,
 CONSTRAINT "formacion_academica_cvlac_id_fk" FOREIGN KEY ("cvlac_id") REFERENCES "public"."identificacion" ("cvlac_id") ON DELETE CASCADE,
 CONSTRAINT "PK_formacion_academica" PRIMARY KEY ("id")
);

-- Crear tabla formacion_complementaria
CREATE TABLE "public"."formacion_complementaria"
(
 "id"                 bigserial,
 "cvlac_id"           varchar NOT NULL,
 "fecha_inicio"       varchar NULL,
 "fecha_fin"          varchar NULL,
 "nivel_formacion"    varchar NULL,
 "institucion"        varchar NULL,
 "programa_academico" varchar NULL,
 CONSTRAINT "formacion_complementaria_cvlac_id_fk" FOREIGN KEY ("cvlac_id") REFERENCES "public"."identificacion" ("cvlac_id") ON DELETE CASCADE,
 CONSTRAINT "PK_formacion_complementaria" PRIMARY KEY ("id")
);

-- Crear tabla experiencia
CREATE TABLE "public"."experiencia"
(
 "id"                 bigserial,
 "cvlac_id"           varchar NOT NULL,
 "institucion"        varchar NULL,
 "ano_inicio"         int NULL,
 "ano_fin"            int NULL,
 "dedicacion"         varchar NULL,
 CONSTRAINT "experiencia_cvlac_id_fk" FOREIGN KEY ("cvlac_id") REFERENCES "public"."identificacion" ("cvlac_id") ON DELETE CASCADE,
 CONSTRAINT "PK_experiencia" PRIMARY KEY ("id")
);

-- Crear tabla areas_actuacion
CREATE TABLE "public"."areas_actuacion"
(
 "id"           bigserial,
 "cvlac_id"     varchar NOT NULL,
 "gran_area"    varchar NULL,
 "area"         varchar NULL,
 "especialidad" varchar NULL,
 CONSTRAINT "areas_actuacion_cvlac_id_fk" FOREIGN KEY ("cvlac_id") REFERENCES "public"."identificacion" ("cvlac_id") ON DELETE CASCADE,
 CONSTRAINT "PK_areas_actuacion" PRIMARY KEY ("id")
);

-- Crear tabla idioma
CREATE TABLE "public"."idioma"
(
 "id"        bigserial,
 "cvlac_id"  varchar NOT NULL,
 "idioma"    varchar NULL,
 "habla"     varchar NULL,
 "lee"       varchar NULL,
 "escribe"   varchar NULL,
 "entiende"  varchar NULL,
 CONSTRAINT "idioma_cvlac_id_fk" FOREIGN KEY ("cvlac_id") REFERENCES "public"."identificacion" ("cvlac_id") ON DELETE CASCADE,
 CONSTRAINT "PK_idioma" PRIMARY KEY ("id")
);

-- Crear tabla lineas_investigacion
CREATE TABLE "public"."lineas_investigacion"
(
 "id"                   bigserial,
 "cvlac_id"             varchar NOT NULL,
 "linea_investigacion"  varchar NULL,
 "activa"               varchar NULL,
 CONSTRAINT "lineas_investigacion_cvlac_id_fk" FOREIGN KEY ("cvlac_id") REFERENCES "public"."identificacion" ("cvlac_id") ON DELETE CASCADE,
 CONSTRAINT "PK_lineas_investigacion" PRIMARY KEY ("id")
);

-- Crear tabla reconocimientos
CREATE TABLE "public"."reconocimientos"
(
 "id"           bigserial,
 "cvlac_id"     varchar NOT NULL,
 "nombre"       varchar NULL,
 "fecha"        varchar NULL,
 "institucion"  varchar NULL,
 CONSTRAINT "reconocimientos_cvlac_id_fk" FOREIGN KEY ("cvlac_id") REFERENCES "public"."identificacion" ("cvlac_id") ON DELETE CASCADE,
 CONSTRAINT "PK_reconocimientos" PRIMARY KEY ("id")
);

-- Crear tabla cursos_corta_duracion
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
 CONSTRAINT "cursos_corta_duracion_cvlac_id_fk" FOREIGN KEY ("cvlac_id") REFERENCES "public"."identificacion" ("cvlac_id") ON DELETE CASCADE,
 CONSTRAINT "PK_cursos_corta_duracion" PRIMARY KEY ("id")
);

-- Crear tabla trabajos_dirigidos
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
 CONSTRAINT "trabajos_dirigidos_cvlac_id_fk" FOREIGN KEY ("cvlac_id") REFERENCES "public"."identificacion" ("cvlac_id") ON DELETE CASCADE,
 CONSTRAINT "PK_trabajos_dirigidos" PRIMARY KEY ("id")
);

-- Crear tabla asesorias
CREATE TABLE "public"."asesorias"
(
 "id"                       bigserial,
 "cvlac_id"                 varchar NOT NULL,
 "chulo"                    varchar NULL,
 "nombre_proyecto_ondas"    varchar NULL,
 "institucion"              varchar NULL,
 "ciudad"                   varchar NULL,
 CONSTRAINT "asesorias_cvlac_id_fk" FOREIGN KEY ("cvlac_id") REFERENCES "public"."identificacion" ("cvlac_id") ON DELETE CASCADE,
 CONSTRAINT "PK_asesorias" PRIMARY KEY ("id")
);

-- Crear tabla jurados
CREATE TABLE "public"."jurados"
(
 "id"                       bigserial,
 "cvlac_id"                 varchar NOT NULL,
 "nivel_programa_academico" varchar NULL,
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
 CONSTRAINT "jurados_cvlac_id_fk" FOREIGN KEY ("cvlac_id") REFERENCES "public"."identificacion" ("cvlac_id") ON DELETE CASCADE,
 CONSTRAINT "PK_jurados" PRIMARY KEY ("id")
);

-- Crear tabla par_evaluador
CREATE TABLE "public"."par_evaluador"
(
 "id"                   bigserial,
 "cvlac_id"             varchar NOT NULL,
 "ambito"               varchar NULL,
 "par_evaluador_de"     varchar NULL,         
 "entidad_convocadora"  varchar NULL,
 "tipo_material"        varchar NULL,
 "ano"                  varchar NULL,
 "mes"                  varchar NULL,
 CONSTRAINT "par_evaluador_cvlac_id_fk" FOREIGN KEY ("cvlac_id") REFERENCES "public"."identificacion" ("cvlac_id") ON DELETE CASCADE,
 CONSTRAINT "PK_par_evaluador" PRIMARY KEY ("id")
);

-- Crear tabla participacion_comites_evaluacion
CREATE TABLE "public"."participacion_comites_evaluacion"
(
 "id"              bigserial,
 "cvlac_id"        varchar NOT NULL,
 "chulo"           varchar NULL,
 "tipo"            varchar NULL,
 "institucion"     varchar NULL,         
 "nombre_producto" varchar NULL,
 "ano"             int NULL,
 CONSTRAINT "participacion_comites_evaluacion_cvlac_id_fk" FOREIGN KEY ("cvlac_id") REFERENCES "public"."identificacion" ("cvlac_id") ON DELETE CASCADE,
 CONSTRAINT "PK_participacion_comites_evaluacion" PRIMARY KEY ("id")
);

-- Crear tabla consultorias
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
 CONSTRAINT "consultorias_cvlac_id_fk" FOREIGN KEY ("cvlac_id") REFERENCES "public"."identificacion" ("cvlac_id") ON DELETE CASCADE,
 CONSTRAINT "PK_consultorias" PRIMARY KEY ("id")
);

-- Crear tabla ediciones_revisiones
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
 CONSTRAINT "ediciones_revisiones_cvlac_id_fk" FOREIGN KEY ("cvlac_id") REFERENCES "public"."identificacion" ("cvlac_id") ON DELETE CASCADE,
 CONSTRAINT "PK_ediciones_revisiones" PRIMARY KEY ("id")
);

-- Crear tabla eventos_cientificos
CREATE TABLE "public"."eventos_cientificos"
(
 "id"               varchar NOT NULL,
 "cvlac_id"         varchar NOT NULL,
 "chulo"            varchar NULL,
 "nombre_evento"    varchar NULL,
 "tipo_evento"      varchar NULL,
 "ambito"           varchar NULL,
 "fecha_inicio"     varchar NULL,
 "fecha_fin"        varchar NULL,
 "ciudad"           varchar NULL,
 "lugar"            varchar NULL,
 "rol"              varchar NULL,
 CONSTRAINT "eventos_cientificos_cvlac_id_fk" FOREIGN KEY ("cvlac_id") REFERENCES "public"."identificacion" ("cvlac_id") ON DELETE CASCADE,
 CONSTRAINT "PK_eventos_cientificos" PRIMARY KEY ("id")
);

-- Crear tabla eventos_participantes
CREATE TABLE "public"."eventos_participantes"
(
 "id"        bigserial,
 "nombre"    varchar NULL,
 "rol"       varchar NULL,
 "evento_id" varchar NOT NULL,
 CONSTRAINT "eventos_participantes_evento_id_fk" FOREIGN KEY ("evento_id") REFERENCES "public"."eventos_cientificos" ("id") ON DELETE CASCADE,
 CONSTRAINT "PK_eventos_participantes" PRIMARY KEY ("id")
);

-- Crear tabla eventos_productos
CREATE TABLE "public"."eventos_productos"
(
 "id"               bigserial,
 "nombre"           varchar NULL,
 "tipo_producto"    varchar NULL,
 "evento_id"        varchar NOT NULL,
 CONSTRAINT "eventos_productos_evento_id_fk" FOREIGN KEY ("evento_id") REFERENCES "public"."eventos_cientificos" ("id") ON DELETE CASCADE,
 CONSTRAINT "PK_eventos_productos" PRIMARY KEY ("id")
);

-- Crear tabla eventos_instituciones
CREATE TABLE "public"."eventos_instituciones"
(
 "id"               bigserial,
 "nombre"           varchar NULL,
 "tipo_vinculacion" varchar NULL,
 "evento_id"        varchar NOT NULL,
 CONSTRAINT "eventos_instituciones_evento_id_fk" FOREIGN KEY ("evento_id") REFERENCES "public"."eventos_cientificos" ("id") ON DELETE CASCADE,
 CONSTRAINT "PK_eventos_instituciones" PRIMARY KEY ("id")
);

-- Crear tabla informes_investigacion
CREATE TABLE "public"."informes_investigacion"
(
 "id"           bigserial,
 "cvlac_id"     varchar NOT NULL,
 "titulo"       varchar NULL,
 "ano"          int NULL,
 "coautores"    varchar NULL,
 CONSTRAINT "informes_investigacion_cvlac_id_fk" FOREIGN KEY ("cvlac_id") REFERENCES "public"."identificacion" ("cvlac_id") ON DELETE CASCADE,
 CONSTRAINT "PK_informes_investigacion" PRIMARY KEY ("id")
);

-- Crear tabla redes_conocimiento
CREATE TABLE "public"."redes_conocimiento"
(
 "id"               bigserial,
 "cvlac_id"         varchar NOT NULL,
 "nombre"           varchar NULL,
 "tipo"             varchar NULL,
 "fecha_inicio"     varchar NULL,
 "lugar"            varchar NULL,
 "participantes"    int NULL,
 CONSTRAINT "redes_conocimiento_cvlac_id_fk" FOREIGN KEY ("cvlac_id") REFERENCES "public"."identificacion" ("cvlac_id") ON DELETE CASCADE,
 CONSTRAINT "PK_redes_conocimiento" PRIMARY KEY ("id")
);

-- Crear tabla audio
CREATE TABLE "public"."audio"
(
 "id"           bigserial,
 "cvlac_id"     varchar NOT NULL,
 "titulo"       varchar NULL,
 "fecha"        varchar NULL,
 "lugar"        varchar NULL,
 "coautores"    varchar NULL,
 "formato"      varchar NULL,
 "descripcion"  varchar NULL,
 "palabras"     varchar NULL,
 "areas"        varchar NULL,
 "sectores"     varchar NULL,
 CONSTRAINT "audio_cvlac_id_fk" FOREIGN KEY ("cvlac_id") REFERENCES "public"."identificacion" ("cvlac_id") ON DELETE CASCADE,
 CONSTRAINT "PK_audio" PRIMARY KEY ("id")
);

-- Crear tabla impresa
CREATE TABLE "public"."impresa"
(
 "id"                   bigserial,
 "cvlac_id"             varchar NOT NULL,
 "nombre"               varchar NULL,
 "tipo"                 varchar NULL,
 "chulo"                varchar NULL,
 "medio_circulacion"    varchar NULL,
 "sitio_web"            varchar NULL,
 "fecha"                varchar NULL,
 "ambito"               varchar NULL,
 CONSTRAINT "impresa_cvlac_id_fk" FOREIGN KEY ("cvlac_id") REFERENCES "public"."identificacion" ("cvlac_id") ON DELETE CASCADE,
 CONSTRAINT "PK_impresa" PRIMARY KEY ("id")
);

-- Crear tabla multimedia
CREATE TABLE "public"."multimedia"
(
 "id"         bigserial,
 "cvlac_id"   varchar NOT NULL,
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
 CONSTRAINT "multimedia_cvlac_id_fk" FOREIGN KEY ("cvlac_id") REFERENCES "public"."identificacion" ("cvlac_id") ON DELETE CASCADE,
 CONSTRAINT "PK_multimedia" PRIMARY KEY ("id")
);

-- Crear tabla secuencias_geneticas
CREATE TABLE "public"."secuencias_geneticas"
(
 "id"               bigserial,
 "cvlac_id"         varchar NOT NULL,
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
 CONSTRAINT "secuencias_geneticas_cvlac_id_fk" FOREIGN KEY ("cvlac_id") REFERENCES "public"."identificacion" ("cvlac_id") ON DELETE CASCADE,
 CONSTRAINT "PK_secuencias_geneticas" PRIMARY KEY ("id")
);

-- Crear tabla contenido_virtual
CREATE TABLE "public"."contenido_virtual"
(
 "id"               bigserial,
 "cvlac_id"         varchar NOT NULL,
 "titulo"           varchar NULL,
 "tipo"             varchar NULL,
 "fecha"            varchar NULL,
 "disponible_en"    varchar NULL,
 "descripcion"      varchar NULL,
 CONSTRAINT "contenido_virtual_cvlac_id_fk" FOREIGN KEY ("cvlac_id") REFERENCES "public"."identificacion" ("cvlac_id") ON DELETE CASCADE,
 CONSTRAINT "PK_contenido_virtual" PRIMARY KEY ("id")
);

-- Crear tabla estrategias_comunicacion
CREATE TABLE "public"."estrategias_comunicacion"
(
 "id"               bigserial,
 "cvlac_id"         varchar NOT NULL,
 "nombre"           varchar NULL,
 "fecha_inicio"     varchar NULL,
 "fecha_fin"        varchar NULL,
 CONSTRAINT "estrategias_comunicacion_cvlac_id_fk" FOREIGN KEY ("cvlac_id") REFERENCES "public"."identificacion" ("cvlac_id") ON DELETE CASCADE,
 CONSTRAINT "PK_estrategias_comunicacion" PRIMARY KEY ("id")
);

-- Crear tabla estrategias_pedagogicas
CREATE TABLE "public"."estrategias_pedagogicas"
(
 "id"               bigserial,
 "cvlac_id"         varchar NOT NULL,
 "nombre"           varchar NULL,
 "fecha_inicio"     varchar NULL,
 "fecha_fin"        varchar NULL,
 CONSTRAINT "estrategias_pedagogicas_cvlac_id_fk" FOREIGN KEY ("cvlac_id") REFERENCES "public"."identificacion" ("cvlac_id") ON DELETE CASCADE,
 CONSTRAINT "PK_estrategias_pedagogicas" PRIMARY KEY ("id")
);

-- Crear tabla espacios_participacion
CREATE TABLE "public"."espacios_participacion"
(
 "id"               bigserial,
 "cvlac_id"         varchar NOT NULL,
 "nombre"           varchar NULL,
 "fecha_inicio"     varchar NULL,
 "fecha_fin"        varchar NULL,
 "ciudad"           varchar NULL,
 "participantes"    int NULL,
 CONSTRAINT "espacios_participacion_cvlac_id_fk" FOREIGN KEY ("cvlac_id") REFERENCES "public"."identificacion" ("cvlac_id") ON DELETE CASCADE,
 CONSTRAINT "PK_espacios_participacion" PRIMARY KEY ("id")
);

-- Crear tabla participacion_proyectos
CREATE TABLE "public"."participacion_proyectos"
(
 "id"               bigserial,
 "cvlac_id"         varchar NOT NULL,
 "nombre"           varchar NULL,
 "fecha_inicio"     varchar NULL,
 "fecha_fin"        varchar NULL,
 CONSTRAINT "participacion_proyectos_cvlac_id_fk" FOREIGN KEY ("cvlac_id") REFERENCES "public"."identificacion" ("cvlac_id") ON DELETE CASCADE,
 CONSTRAINT "PK_participacion_proyectos" PRIMARY KEY ("id")
);

-- Crear tabla obras_productos
CREATE TABLE "public"."obras_productos"
(
 "id"             bigserial,
 "cvlac_id"       varchar NOT NULL,
 "chulo"          varchar NULL,
 "nombre"         varchar NULL,
 "disciplina"     varchar NULL,
 "fecha_creacion" varchar NULL,
 CONSTRAINT "obras_productos_cvlac_id_fk" FOREIGN KEY ("cvlac_id") REFERENCES "public"."identificacion" ("cvlac_id") ON DELETE CASCADE,
 CONSTRAINT "PK_obras_productos" PRIMARY KEY ("id")
);

-- Crear tabla registro_licencia
CREATE TABLE "public"."registro_licencia"
(
 "id"                  bigserial,
 "cvlac_id"            varchar NOT NULL,
 "chulo"               varchar NULL,
 "institucion"         varchar NULL,
 "fecha_otorgamiento"  varchar NULL,
 "numero_registro"     varchar NULL,
 "nacional_derechos"   varchar NULL,
 CONSTRAINT "registro_licencia_cvlac_id_fk" FOREIGN KEY ("cvlac_id") REFERENCES "public"."identificacion" ("cvlac_id") ON DELETE CASCADE,
 CONSTRAINT "PK_registro_licencia" PRIMARY KEY ("id")
);

-- Crear tabla industrias_creativas_culturales
CREATE TABLE "public"."industrias_creativas_culturales"
(
 "id"               bigserial,
 "cvlac_id"         varchar NOT NULL,
 "nombre"           varchar NULL,
 "nit_registro"     varchar NULL,
 "fecha_registro"   varchar NULL,
 "tiene_productos"  varchar NULL,
 CONSTRAINT "industrias_creativas_culturales_cvlac_id_fk" FOREIGN KEY ("cvlac_id") REFERENCES "public"."identificacion" ("cvlac_id") ON DELETE CASCADE,
 CONSTRAINT "PK_industrias_creativas_culturales" PRIMARY KEY ("id")
);

-- Crear tabla eventos_artisticos
CREATE TABLE "public"."eventos_artisticos"
(
 "id"             bigserial,
 "cvlac_id"       varchar NOT NULL,
 "chulo"          varchar NULL,
 "nombre"         varchar NULL,
 "fecha_inicio"   varchar NULL,
 CONSTRAINT "eventos_artisticos_cvlac_id_fk" FOREIGN KEY ("cvlac_id") REFERENCES "public"."identificacion" ("cvlac_id") ON DELETE CASCADE,
 CONSTRAINT "PK_eventos_artisticos" PRIMARY KEY ("id")
);

-- Crear tabla talleres_creativos
CREATE TABLE "public"."talleres_creativos"
(
 "id"                   bigserial,
 "cvlac_id"             varchar NOT NULL,
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
 CONSTRAINT "talleres_creativos_cvlac_id_fk" FOREIGN KEY ("cvlac_id") REFERENCES "public"."identificacion" ("cvlac_id") ON DELETE CASCADE,
 CONSTRAINT "PK_talleres_creativos" PRIMARY KEY ("id")
);

-- Crear tabla articulos
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
 CONSTRAINT "articulos_cvlac_id_fk" FOREIGN KEY ("cvlac_id") REFERENCES "public"."identificacion" ("cvlac_id") ON DELETE CASCADE,
 CONSTRAINT "PK_articulos" PRIMARY KEY ("id")
);

-- Crear tabla articulos_publicados (similar a articulos pero con distinta estructura)
CREATE TABLE "public"."articulos_publicados"
(
 "id"                  bigserial,
 "cvlac_id"            varchar NOT NULL,
 "chulo"               varchar NULL,
 "tipo"                varchar NULL,
 "coautores"           varchar NULL,
 "titulo"              varchar NULL,
 "pais"                varchar NULL,
 "issn"                varchar NULL,
 "editorial"           varchar NULL,
 "volumen"             varchar NULL,
 "fasciculo"           varchar NULL,
 "pagina_inicial"      int NULL,
 "pagina_final"        int NULL,
 "ano"                 int NULL,
 "doi"                 varchar NULL,
 "palabras"            varchar NULL,
 CONSTRAINT "articulos_publicados_cvlac_id_fk" FOREIGN KEY ("cvlac_id") REFERENCES "public"."identificacion" ("cvlac_id") ON DELETE CASCADE,
 CONSTRAINT "PK_articulos_publicados" PRIMARY KEY ("id")
);

-- Crear tabla capitulos_libro
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
 CONSTRAINT "capitulos_libro_cvlac_id_fk" FOREIGN KEY ("cvlac_id") REFERENCES "public"."identificacion" ("cvlac_id") ON DELETE CASCADE,
 CONSTRAINT "PK_capitulos_libro" PRIMARY KEY ("id")
);

-- Crear tabla libros
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
 CONSTRAINT "libros_cvlac_id_fk" FOREIGN KEY ("cvlac_id") REFERENCES "public"."identificacion" ("cvlac_id") ON DELETE CASCADE,
 CONSTRAINT "PK_libros" PRIMARY KEY ("id")
);

-- Crear tabla documentos_trabajo
CREATE TABLE "public"."documentos_trabajo"
(
 "id"         bigserial,
 "cvlac_id"   varchar NOT NULL,
 "nombre"     varchar NULL,
 "ano"        int NULL,
 "paginas"    varchar NULL,
 CONSTRAINT "documentos_trabajo_cvlac_id_fk" FOREIGN KEY ("cvlac_id") REFERENCES "public"."identificacion" ("cvlac_id") ON DELETE CASCADE,
 CONSTRAINT "PK_documentos_trabajo" PRIMARY KEY ("id")
);

-- Crear tabla otra_produccion
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
 CONSTRAINT "otra_produccion_cvlac_id_fk" FOREIGN KEY ("cvlac_id") REFERENCES "public"."identificacion" ("cvlac_id") ON DELETE CASCADE,
 CONSTRAINT "PK_otra_produccion" PRIMARY KEY ("id")
);

-- Crear tabla textos_no_cientificas
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
 "volumen"          varchar NULL,
 "palabras"         varchar NULL,
 "areas"            varchar NULL,
 "sectores"         varchar NULL,
 CONSTRAINT "textos_no_cientificas_cvlac_id_fk" FOREIGN KEY ("cvlac_id") REFERENCES "public"."identificacion" ("cvlac_id") ON DELETE CASCADE,
 CONSTRAINT "PK_textos_no_cientificas" PRIMARY KEY ("id")
);

-- Crear tabla traducciones
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
 "volumen"              varchar NULL,
 "palabras"             varchar NULL,
 "areas"                varchar NULL,
 "sectores"             varchar NULL,
 CONSTRAINT "traducciones_cvlac_id_fk" FOREIGN KEY ("cvlac_id") REFERENCES "public"."identificacion" ("cvlac_id") ON DELETE CASCADE,
 CONSTRAINT "PK_traducciones" PRIMARY KEY ("id")
);

-- Crear tabla notas_cientificas
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
 "volumen"              varchar NULL,
 "fasc"                 varchar NULL,
 "pagina_inicial"       int NULL,
 "pagina_final"         int NULL,
 "ano"                  int NULL,
 "sitio_web"            varchar NULL,
 "doi"                  varchar NULL,
 "palabras"             varchar NULL,
 "areas"                varchar NULL,
 "sectores"             varchar NULL,
 CONSTRAINT "notas_cientificas_cvlac_id_fk" FOREIGN KEY ("cvlac_id") REFERENCES "public"."identificacion" ("cvlac_id") ON DELETE CASCADE,
 CONSTRAINT "PK_notas_cientificas" PRIMARY KEY ("id")
);

-- Crear tabla cartas_mapas
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
 CONSTRAINT "cartas_mapas_cvlac_id_fk" FOREIGN KEY ("cvlac_id") REFERENCES "public"."identificacion" ("cvlac_id") ON DELETE CASCADE,
 CONSTRAINT "PK_cartas_mapas" PRIMARY KEY ("id")
);

-- Crear tabla conceptos_tecnicos
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
 CONSTRAINT "conceptos_tecnicos_cvlac_id_fk" FOREIGN KEY ("cvlac_id") REFERENCES "public"."identificacion" ("cvlac_id") ON DELETE CASCADE,
 CONSTRAINT "PK_conceptos_tecnicos" PRIMARY KEY ("id")
);

-- Crear tabla diseno_industrial
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
 CONSTRAINT "diseno_industrial_cvlac_id_fk" FOREIGN KEY ("cvlac_id") REFERENCES "public"."identificacion" ("cvlac_id") ON DELETE CASCADE,
 CONSTRAINT "PK_diseno_industrial" PRIMARY KEY ("id")
);

-- Crear tabla empresas_base_tecnologica
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
 CONSTRAINT "empresas_base_tecnologica_cvlac_id_fk" FOREIGN KEY ("cvlac_id") REFERENCES "public"."identificacion" ("cvlac_id") ON DELETE CASCADE,
 CONSTRAINT "PK_empresas_base_tecnologica" PRIMARY KEY ("id")
);

-- Crear tabla esquemas_trazado
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
 CONSTRAINT "esquemas_trazado_cvlac_id_fk" FOREIGN KEY ("cvlac_id") REFERENCES "public"."identificacion" ("cvlac_id") ON DELETE CASCADE,
 CONSTRAINT "PK_esquemas_trazado" PRIMARY KEY ("id")
);

-- Crear tabla informes_tecnicos
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
 CONSTRAINT "informes_tecnicos_cvlac_id_fk" FOREIGN KEY ("cvlac_id") REFERENCES "public"."identificacion" ("cvlac_id") ON DELETE CASCADE,
 CONSTRAINT "PK_informes_tecnicos" PRIMARY KEY ("id")
);

-- Crear tabla innovacion_procesos
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
 CONSTRAINT "innovacion_procesos_cvlac_id_fk" FOREIGN KEY ("cvlac_id") REFERENCES "public"."identificacion" ("cvlac_id") ON DELETE CASCADE,
 CONSTRAINT "PK_innovacion_procesos" PRIMARY KEY ("id")
);

-- Crear tabla innovacion_gestion
CREATE TABLE "public"."innovacion_gestion"
(
 "id"                  bigserial,
 "cvlac_id"            varchar NOT NULL,
 "tipo"                varchar NULL,
 "coautores"           varchar NULL,
 "nombre"              varchar NULL,
 "pais"                varchar NULL,
 "ano"                 int NULL,
 "palabras"            varchar NULL,
 "areas"               varchar NULL,
 "sectores"            varchar NULL,
 CONSTRAINT "innovacion_gestion_cvlac_id_fk" FOREIGN KEY ("cvlac_id") REFERENCES "public"."identificacion" ("cvlac_id") ON DELETE CASCADE,
 CONSTRAINT "PK_innovacion_gestion" PRIMARY KEY ("id")
);

-- Crear tabla variedad_animal
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
 CONSTRAINT "variedad_animal_cvlac_id_fk" FOREIGN KEY ("cvlac_id") REFERENCES "public"."identificacion" ("cvlac_id") ON DELETE CASCADE,
 CONSTRAINT "PK_variedad_animal" PRIMARY KEY ("id")
);

-- Crear tabla poblaciones_mejoradas
CREATE TABLE "public"."poblaciones_mejoradas"
(
 "id"                   bigserial,
 "cvlac_id"             varchar NOT NULL,
 "coautores"            varchar NULL,
 "nombre"               varchar NULL,
 "pais"                 varchar NULL,
 "ano"                  int NULL,
 "numero_certificado"   varchar NULL,
 CONSTRAINT "poblaciones_mejoradas_cvlac_id_fk" FOREIGN KEY ("cvlac_id") REFERENCES "public"."identificacion" ("cvlac_id") ON DELETE CASCADE,
 CONSTRAINT "PK_poblaciones_mejoradas" PRIMARY KEY ("id")
);

-- Crear tabla variedad_vegetal
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
 CONSTRAINT "variedad_vegetal_cvlac_id_fk" FOREIGN KEY ("cvlac_id") REFERENCES "public"."identificacion" ("cvlac_id") ON DELETE CASCADE,
 CONSTRAINT "PK_variedad_vegetal" PRIMARY KEY ("id")
);

-- Crear tabla registro_cientifico
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
 CONSTRAINT "registro_cientifico_cvlac_id_fk" FOREIGN KEY ("cvlac_id") REFERENCES "public"."identificacion" ("cvlac_id") ON DELETE CASCADE,
 CONSTRAINT "PK_registro_cientifico" PRIMARY KEY ("id")
);

-- Crear tabla plantas_piloto
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
 CONSTRAINT "plantas_piloto_cvlac_id_fk" FOREIGN KEY ("cvlac_id") REFERENCES "public"."identificacion" ("cvlac_id") ON DELETE CASCADE,
 CONSTRAINT "PK_plantas_piloto" PRIMARY KEY ("id")
);

-- Crear tabla productos_nutraceuticos
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
 "numero_registro"      varchar NULL,
 "numero_contrato"      varchar NULL,         
 "proyecto_vinculado"   varchar NULL,
 CONSTRAINT "productos_nutraceuticos_cvlac_id_fk" FOREIGN KEY ("cvlac_id") REFERENCES "public"."identificacion" ("cvlac_id") ON DELETE CASCADE,
 CONSTRAINT "PK_productos_nutraceuticos" PRIMARY KEY ("id")
);

-- Crear tabla productos_tecnologicos
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
 CONSTRAINT "productos_tecnologicos_cvlac_id_fk" FOREIGN KEY ("cvlac_id") REFERENCES "public"."identificacion" ("cvlac_id") ON DELETE CASCADE,
 CONSTRAINT "PK_productos_tecnologicos" PRIMARY KEY ("id")
);

-- Crear tabla prototipos
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
 CONSTRAINT "prototipos_cvlac_id_fk" FOREIGN KEY ("cvlac_id") REFERENCES "public"."identificacion" ("cvlac_id") ON DELETE CASCADE,
 CONSTRAINT "PK_prototipos" PRIMARY KEY ("id")
);

-- Crear tabla normas_regulaciones
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
 CONSTRAINT "normas_regulaciones_cvlac_id_fk" FOREIGN KEY ("cvlac_id") REFERENCES "public"."identificacion" ("cvlac_id") ON DELETE CASCADE,
 CONSTRAINT "PK_normas_regulaciones" PRIMARY KEY ("id")
);

-- Crear tabla protocolos_vigilancia
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
 CONSTRAINT "protocolos_vigilancia_cvlac_id_fk" FOREIGN KEY ("cvlac_id") REFERENCES "public"."identificacion" ("cvlac_id") ON DELETE CASCADE,
 CONSTRAINT "PK_protocolos_vigilancia" PRIMARY KEY ("id")
);

-- Crear tabla reglamentos
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
 CONSTRAINT "reglamentos_cvlac_id_fk" FOREIGN KEY ("cvlac_id") REFERENCES "public"."identificacion" ("cvlac_id") ON DELETE CASCADE,
 CONSTRAINT "PK_reglamentos" PRIMARY KEY ("id")
);

-- Crear tabla signos_distintivos
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
 "titular"            varchar NULL,
 CONSTRAINT "signos_distintivos_cvlac_id_fk" FOREIGN KEY ("cvlac_id") REFERENCES "public"."identificacion" ("cvlac_id") ON DELETE CASCADE,
 CONSTRAINT "PK_signos_distintivos" PRIMARY KEY ("id")
);

-- Crear tabla software
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
 "plataforma"         varchar NULL,
 "ambiente"           varchar NULL,
 "palabras"           varchar NULL,
 "areas"              varchar NULL,
 "sectores"           varchar NULL,
 CONSTRAINT "software_cvlac_id_fk" FOREIGN KEY ("cvlac_id") REFERENCES "public"."identificacion" ("cvlac_id") ON DELETE CASCADE,
 CONSTRAINT "PK_software" PRIMARY KEY ("id")
);

-- Crear tabla demas_trabajos
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
 CONSTRAINT "demas_trabajos_cvlac_id_fk" FOREIGN KEY ("cvlac_id") REFERENCES "public"."identificacion" ("cvlac_id") ON DELETE CASCADE,
 CONSTRAINT "PK_demas_trabajos" PRIMARY KEY ("id")
);

-- Crear tabla proyectos
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
 "resumen"      text NULL,
 CONSTRAINT "proyectos_cvlac_id_fk" FOREIGN KEY ("cvlac_id") REFERENCES "public"."identificacion" ("cvlac_id") ON DELETE CASCADE,
 CONSTRAINT "PK_proyectos" PRIMARY KEY ("id")
);

-- Crear tabla redes_sociales
CREATE TABLE "public"."redes_sociales"
(
 "id"                 bigserial,
 "cvlac_id"           varchar NOT NULL,
 "red"                varchar NULL,
 "link"               varchar NULL,
 CONSTRAINT "redes_sociales_cvlac_id_fk" FOREIGN KEY ("cvlac_id") REFERENCES "public"."identificacion" ("cvlac_id") ON DELETE CASCADE,
 CONSTRAINT "PK_redes_sociales" PRIMARY KEY ("id")
);

-- Crear tabla investigador_grupo para integración con GrupLAC
CREATE TABLE "public"."investigador_grupo"
(
    "cvlac_id" VARCHAR NOT NULL,
    "grupo_id" VARCHAR NOT NULL,
    "nombre_grupo" VARCHAR NULL,
    "clasificacion" VARCHAR NULL,
    "nombre_investigador" VARCHAR NULL,
    "fecha_actualizacion" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY ("cvlac_id", "grupo_id"),
    CONSTRAINT "investigador_grupo_cvlac_id_fk" FOREIGN KEY ("cvlac_id") REFERENCES "public"."identificacion" ("cvlac_id") ON DELETE CASCADE
);

-- Crear índices para mejorar el rendimiento
CREATE INDEX idx_formacion_academica_cvlac ON formacion_academica(cvlac_id);
CREATE INDEX idx_formacion_complementaria_cvlac ON formacion_complementaria(cvlac_id);
CREATE INDEX idx_experiencia_cvlac ON experiencia(cvlac_id);
CREATE INDEX idx_areas_actuacion_cvlac ON areas_actuacion(cvlac_id);
CREATE INDEX idx_idioma_cvlac ON idioma(cvlac_id);
CREATE INDEX idx_lineas_investigacion_cvlac ON lineas_investigacion(cvlac_id);
CREATE INDEX idx_reconocimientos_cvlac ON reconocimientos(cvlac_id);
CREATE INDEX idx_eventos_cientificos_cvlac ON eventos_cientificos(cvlac_id);
CREATE INDEX idx_articulos_publicados_cvlac ON articulos_publicados(cvlac_id);
CREATE INDEX idx_eventos_artisticos_cvlac ON eventos_artisticos(cvlac_id);
CREATE INDEX idx_proyectos_cvlac ON proyectos(cvlac_id);
CREATE INDEX idx_articulos_cvlac ON articulos(cvlac_id);
CREATE INDEX idx_libros_cvlac ON libros(cvlac_id);
CREATE INDEX idx_capitulos_libro_cvlac ON capitulos_libro(cvlac_id);
CREATE INDEX idx_software_cvlac ON software(cvlac_id);

-- Restaurar notificaciones a su nivel normal
SET client_min_messages TO DEFAULT;

-- Mensaje final
SELECT 'Schema CvLAC creado con éxito' AS mensaje;