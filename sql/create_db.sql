--
-- PostgreSQL database dump
--

-- Dumped from database version 16.8 (Debian 16.8-1.pgdg120+1)
-- Dumped by pg_dump version 17.0 (Ubuntu 17.0-1.pgdg22.04+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: public; Type: SCHEMA; Schema: -; Owner: postgres
--

-- *not* creating schema, since initdb creates it


ALTER SCHEMA public OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: articulos_publicados; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.articulos_publicados (
    nro character varying NOT NULL,
    consecutivo integer NOT NULL,
    chulo character varying NOT NULL,
    tipo character varying,
    titulo character varying,
    pais character varying,
    revista character varying,
    issn character varying,
    volumen character varying,
    fasciculo character varying,
    paginas character varying,
    ano integer,
    doi character varying,
    autores character varying
);


ALTER TABLE public.articulos_publicados OWNER TO postgres;

--
-- Name: capitulos_libro; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.capitulos_libro (
    nro character varying NOT NULL,
    consecutivo integer NOT NULL,
    chulo character varying NOT NULL,
    tipo character varying,
    titulo character varying,
    pais character varying,
    isbn character varying,
    volumen character varying,
    paginas character varying,
    ano integer,
    libro character varying,
    editorial character varying,
    autores character varying
);


ALTER TABLE public.capitulos_libro OWNER TO postgres;

--
-- Name: cartas_mapas; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.cartas_mapas (
    nro character varying NOT NULL,
    consecutivo integer NOT NULL,
    chulo character varying NOT NULL,
    tipo character varying,
    nombre character varying,
    pais character varying,
    ano integer,
    institucion_financiadora character varying NOT NULL,
    tema character varying,
    autores character varying
);


ALTER TABLE public.cartas_mapas OWNER TO postgres;

--
-- Name: conceptos_tecnicos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.conceptos_tecnicos (
    nro character varying NOT NULL,
    consecutivo integer NOT NULL,
    chulo character varying NOT NULL,
    tipo character varying,
    nombre character varying,
    ano integer,
    mes integer,
    fecha_envio date,
    institucion_solicitante character varying,
    ciudad character varying,
    numero_concepto character varying
);


ALTER TABLE public.conceptos_tecnicos OWNER TO postgres;

--
-- Name: consultorias_cientificas; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.consultorias_cientificas (
    nro character varying,
    consecutivo integer NOT NULL,
    chulo character varying NOT NULL,
    nombre character varying,
    ano_inicio integer,
    mes_inicio integer,
    ano_fin integer,
    mes_fin integer,
    idioma character varying,
    ciudad character varying,
    disponibilidad character varying,
    duracion character varying,
    numero_contrato character varying,
    institucion character varying
);


ALTER TABLE public.consultorias_cientificas OWNER TO postgres;

--
-- Name: curso_corta_duracion; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.curso_corta_duracion (
    nro character varying,
    consecutivo integer NOT NULL,
    nombre character varying,
    tipo character varying,
    idioma character varying,
    pais character varying,
    ano integer,
    medio_divulgacion character varying,
    sitio_web character varying,
    duracion integer,
    finalidad character varying,
    lugar character varying,
    institucion_financiadora character varying,
    autores character varying
);


ALTER TABLE public.curso_corta_duracion OWNER TO postgres;

--
-- Name: curso_doctorado; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.curso_doctorado (
    nro character varying NOT NULL,
    "Nombre del Curso" character varying,
    "Fecha acto administrativo curso" date,
    "Número acto administrativo curso" character varying,
    "Programa académico" character varying
);


ALTER TABLE public.curso_doctorado OWNER TO postgres;

--
-- Name: curso_maestria; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.curso_maestria (
    nro character varying NOT NULL,
    consecutivo integer NOT NULL,
    "Nombre del Curso" character varying,
    "Fecha acto administrativo curso" date,
    "Número acto administrativo curso" character varying,
    "Programa académico" character varying
);


ALTER TABLE public.curso_maestria OWNER TO postgres;

--
-- Name: cursos_especializados_extension; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.cursos_especializados_extension (
    nro character varying NOT NULL,
    consecutivo integer NOT NULL,
    "Nombre del Curso" character varying,
    "Fecha acto administrativo curso" date,
    "Número acto administrativo curso" character varying,
    "Programa académico" character varying
);


ALTER TABLE public.cursos_especializados_extension OWNER TO postgres;

--
-- Name: datos_basicos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.datos_basicos (
    nro character varying NOT NULL,
    nombre character varying,
    "Año y mes de formación" date,
    "Departamento - Ciudad" character varying,
    "Líder" character varying,
    "¿La información de este grupo se ha certificado?" character varying,
    "Página web" character varying,
    "E-mail" character varying,
    "Clasificación" character varying,
    "Área de conocimiento" character varying,
    "Programa nacional de ciencia y tecnología" character varying,
    "Programa nacional de ciencia y tecnología (secundario)" character varying
);


ALTER TABLE public.datos_basicos OWNER TO postgres;

--
-- Name: demas_trabajos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.demas_trabajos (
    nro character varying,
    consecutivo integer NOT NULL,
    nombre character varying,
    idioma character varying,
    pais character varying,
    ano integer,
    medio_divulgacion character varying,
    autores character varying
);


ALTER TABLE public.demas_trabajos OWNER TO postgres;

--
-- Name: disenos_industriales; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.disenos_industriales (
    nro character varying NOT NULL,
    consecutivo integer NOT NULL,
    chulo character varying NOT NULL,
    tipo character varying,
    nombre character varying,
    pais character varying,
    ano integer,
    disponibilidad character varying,
    institucion_financiadora character varying,
    autores character varying
);


ALTER TABLE public.disenos_industriales OWNER TO postgres;

--
-- Name: documentos_trabajo; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.documentos_trabajo (
    nro character varying NOT NULL,
    consecutivo integer NOT NULL,
    nombre character varying,
    ano integer,
    paginas character varying,
    instituciones character varying,
    url character varying,
    doi character varying,
    autores character varying
);


ALTER TABLE public.documentos_trabajo OWNER TO postgres;

--
-- Name: ediciones; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.ediciones (
    nro character varying,
    consecutivo integer NOT NULL,
    chulo character varying NOT NULL,
    tipo character varying,
    nombre character varying,
    pais character varying,
    ano integer,
    editorial character varying,
    idiomas character varying,
    paginas integer,
    autores character varying
);


ALTER TABLE public.ediciones OWNER TO postgres;

--
-- Name: empresas_base_tecnologica; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.empresas_base_tecnologica (
    nro character varying NOT NULL,
    consecutivo integer NOT NULL,
    chulo character varying NOT NULL,
    tipo character varying,
    nombre character varying,
    nit character varying,
    fecha_registro date,
    tiene_productos_mercado character varying,
    autores character varying
);


ALTER TABLE public.empresas_base_tecnologica OWNER TO postgres;

--
-- Name: espacios_participacion_ciudadana; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.espacios_participacion_ciudadana (
    nro character varying,
    consecutivo integer NOT NULL,
    nombre character varying,
    ciudad character varying,
    fecha_inicio date,
    fecha_fin date,
    participantes integer,
    sitio_web character varying
);


ALTER TABLE public.espacios_participacion_ciudadana OWNER TO postgres;

--
-- Name: estrategias_comunicacion_conocimiento; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.estrategias_comunicacion_conocimiento (
    nro character varying,
    consecutivo integer NOT NULL,
    nombre character varying,
    fecha_inicio date,
    fecha_fin date,
    descripcion character varying
);


ALTER TABLE public.estrategias_comunicacion_conocimiento OWNER TO postgres;

--
-- Name: estrategias_pedagogicas; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.estrategias_pedagogicas (
    nro character varying,
    consecutivo integer NOT NULL,
    nombre character varying,
    fecha_inicio date,
    fecha_fin date,
    descripcion character varying
);


ALTER TABLE public.estrategias_pedagogicas OWNER TO postgres;

--
-- Name: eventos_artisticos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.eventos_artisticos (
    nro character varying,
    nombre character varying,
    chulo character varying NOT NULL,
    fecha_inicio date,
    fecha_fin date,
    descripcion character varying
);


ALTER TABLE public.eventos_artisticos OWNER TO postgres;

--
-- Name: eventos_cientificos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.eventos_cientificos (
    nro character varying,
    consecutivo integer NOT NULL,
    chulo character varying NOT NULL,
    instituciones_asociadas character varying NOT NULL,
    nombre character varying,
    tipo character varying,
    ambito character varying,
    fecha_inicio date,
    fecha_fin date,
    ciudad character varying,
    "tipos_participación" character varying
);


ALTER TABLE public.eventos_cientificos OWNER TO postgres;

--
-- Name: generaciones_contenido_audio; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.generaciones_contenido_audio (
    nro character varying,
    consecutivo integer NOT NULL,
    chulo character varying NOT NULL,
    mes_ano character varying,
    disponible_en character varying,
    nombre character varying,
    ano integer,
    mes integer,
    ciudad character varying,
    formato character varying,
    descripcion character varying
);


ALTER TABLE public.generaciones_contenido_audio OWNER TO postgres;

--
-- Name: generaciones_contenido_impreso; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.generaciones_contenido_impreso (
    nro character varying,
    consecutivo integer NOT NULL,
    chulo character varying NOT NULL,
    nombre character varying,
    tipo character varying,
    ambito character varying,
    fecha date,
    medio_circulacion character varying,
    lugar character varying,
    sitio_web character varying,
    autores character varying
);


ALTER TABLE public.generaciones_contenido_impreso OWNER TO postgres;

--
-- Name: generaciones_contenido_multimedia; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.generaciones_contenido_multimedia (
    nro character varying,
    consecutivo integer NOT NULL,
    nombre character varying,
    tipo character varying,
    idioma character varying,
    pais character varying,
    ano integer,
    medio_divulgacion character varying,
    sitio_web character varying,
    emisora character varying,
    instituciones character varying,
    autores character varying
);


ALTER TABLE public.generaciones_contenido_multimedia OWNER TO postgres;

--
-- Name: generaciones_contenido_virtual; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.generaciones_contenido_virtual (
    nro character varying,
    consecutivo integer NOT NULL,
    nombre character varying,
    tipo character varying,
    entidades character varying,
    fecha date,
    sitio_web character varying,
    autores character varying
);


ALTER TABLE public.generaciones_contenido_virtual OWNER TO postgres;

--
-- Name: industrias_creativas_culturales; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.industrias_creativas_culturales (
    nro character varying,
    nombre character varying,
    chulo character varying NOT NULL,
    nit_codigo character varying,
    fecha date,
    tiene_productos_mercado character varying
);


ALTER TABLE public.industrias_creativas_culturales OWNER TO postgres;

--
-- Name: informes_investigacion; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.informes_investigacion (
    nro character varying,
    consecutivo integer NOT NULL,
    chulo character varying NOT NULL,
    nombre character varying,
    ano integer,
    proyecto character varying,
    autores character varying
);


ALTER TABLE public.informes_investigacion OWNER TO postgres;

--
-- Name: informes_tecnicos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.informes_tecnicos (
    nro character varying NOT NULL,
    consecutivo integer NOT NULL,
    tipo character varying,
    nombre character varying,
    ano integer,
    mes integer,
    idioma character varying,
    ciudad character varying,
    disponibilidad character varying,
    numero_paginas character varying,
    numero_contrato character varying,
    institucion character varying
);


ALTER TABLE public.informes_tecnicos OWNER TO postgres;

--
-- Name: innovaciones_procesos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.innovaciones_procesos (
    nro character varying NOT NULL,
    consecutivo integer NOT NULL,
    chulo character varying NOT NULL,
    tipo character varying,
    nombre character varying,
    pais character varying,
    ano integer,
    disponibilidad character varying,
    institucion character varying,
    autores character varying
);


ALTER TABLE public.innovaciones_procesos OWNER TO postgres;

--
-- Name: instituciones; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.instituciones (
    nro character varying NOT NULL,
    nombre character varying
);


ALTER TABLE public.instituciones OWNER TO postgres;

--
-- Name: integrantes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.integrantes (
    nro character varying NOT NULL,
    nombre character varying,
    url_cvlac character varying,
    vinculacion character varying,
    horas_dedicacion integer,
    inicio_fin_vinculacion character varying
);


ALTER TABLE public.integrantes OWNER TO postgres;

--
-- Name: jurados; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.jurados (
    nro character varying,
    tipo character varying,
    titulo character varying,
    medio_divulgacion character varying,
    pais character varying,
    ano integer,
    idioma character varying,
    sitio_web character varying,
    nombre_orientado character varying,
    programa character varying,
    institucion character varying,
    autores character varying
);


ALTER TABLE public.jurados OWNER TO postgres;

--
-- Name: libros_publicados; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.libros_publicados (
    nro character varying NOT NULL,
    consecutivo integer NOT NULL,
    chulo character varying NOT NULL,
    tipo character varying,
    titulo character varying,
    pais character varying,
    isbn character varying,
    volumen character varying,
    paginas character varying,
    ano integer,
    editorial character varying,
    autores character varying
);


ALTER TABLE public.libros_publicados OWNER TO postgres;

--
-- Name: lineas_investigacion; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.lineas_investigacion (
    nro character varying NOT NULL,
    nombre character varying
);


ALTER TABLE public.lineas_investigacion OWNER TO postgres;

--
-- Name: nuevas_secuencias_geneticas; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.nuevas_secuencias_geneticas (
    nro character varying,
    chulo character varying NOT NULL,
    nombre character varying,
    ano integer,
    mes integer,
    ciudad character varying,
    base_datos character varying,
    sitio_web character varying,
    institucion_certificadora character varying
);


ALTER TABLE public.nuevas_secuencias_geneticas OWNER TO postgres;

--
-- Name: nuevas_variedades; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.nuevas_variedades (
    nro character varying NOT NULL,
    consecutivo integer NOT NULL,
    chulo character varying NOT NULL,
    tipo character varying,
    nombre character varying,
    pais character varying,
    ano integer,
    tipo_ciclo character varying,
    sitio_web character varying NOT NULL,
    institucion character varying,
    autores character varying
);


ALTER TABLE public.nuevas_variedades OWNER TO postgres;

--
-- Name: obras_productos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.obras_productos (
    nro character varying,
    nombre character varying,
    chulo character varying NOT NULL,
    fecha date,
    disciplina character varying,
    instancias_valoracion character varying,
    registros_acuerdo_licencia character varying
);


ALTER TABLE public.obras_productos OWNER TO postgres;

--
-- Name: otra_pubicacion_divulgativa; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.otra_pubicacion_divulgativa (
    nro character varying NOT NULL,
    tipo character varying,
    titulo character varying,
    pais character varying,
    volumen character varying,
    paginas character varying,
    ano integer,
    editorial character varying,
    autores character varying
);


ALTER TABLE public.otra_pubicacion_divulgativa OWNER TO postgres;

--
-- Name: otros_productos_tec; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.otros_productos_tec (
    nro character varying NOT NULL,
    nombre character varying,
    pais character varying,
    ano integer,
    disponibilidad character varying,
    nombre_comercial character varying NOT NULL,
    institucion character varying,
    autores character varying
);


ALTER TABLE public.otros_productos_tec OWNER TO postgres;

--
-- Name: otros_programas_academicos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.otros_programas_academicos (
    nro character varying NOT NULL,
    "Programa académico" character varying,
    "Fecha acto administrativo programa" date,
    "Número acto administrativo programa" character varying,
    "Institución" character varying
);


ALTER TABLE public.otros_programas_academicos OWNER TO postgres;

--
-- Name: participacion_comites; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.participacion_comites (
    nro character varying,
    tipo character varying,
    nombre character varying,
    pais character varying,
    ano integer,
    sitio_web character varying,
    medio_divulgacion character varying,
    institucion character varying,
    autores character varying
);


ALTER TABLE public.participacion_comites OWNER TO postgres;

--
-- Name: participacion_cti; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.participacion_cti (
    nro character varying,
    nombre character varying,
    fecha_inicio date,
    fecha_fin date,
    descripcion character varying
);


ALTER TABLE public.participacion_cti OWNER TO postgres;

--
-- Name: plan_estrategico; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.plan_estrategico (
    nro character varying NOT NULL,
    "Plan de trabajo" character varying,
    "Estado del arte" character varying,
    "Objetivos" character varying,
    "Retos" character varying,
    "Visión" character varying
);


ALTER TABLE public.plan_estrategico OWNER TO postgres;

--
-- Name: plantas_piloto; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.plantas_piloto (
    nro character varying NOT NULL,
    nombre character varying,
    pais character varying,
    ano integer,
    disponibilidad character varying,
    nombre_comercial character varying NOT NULL,
    institucion character varying,
    autores character varying
);


ALTER TABLE public.plantas_piloto OWNER TO postgres;

--
-- Name: programas_doctorado; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.programas_doctorado (
    nro character varying NOT NULL,
    "Programa académico" character varying,
    "Fecha acto administrativo programa" date,
    "Número acto administrativo programa" character varying,
    "Institución" character varying
);


ALTER TABLE public.programas_doctorado OWNER TO postgres;

--
-- Name: programas_maestria; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.programas_maestria (
    nro character varying NOT NULL,
    "Programa académico" character varying,
    "Fecha acto administrativo programa" date,
    "Número acto administrativo programa" character varying,
    "Institución" character varying
);


ALTER TABLE public.programas_maestria OWNER TO postgres;

--
-- Name: prototipos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.prototipos (
    nro character varying NOT NULL,
    consecutivo integer NOT NULL,
    chulo character varying NOT NULL,
    nombre character varying,
    pais character varying,
    ano integer,
    disponibilidad character varying,
    institucion character varying,
    autores character varying
);


ALTER TABLE public.prototipos OWNER TO postgres;

--
-- Name: proyectos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.proyectos (
    nro character varying,
    consecutivo integer NOT NULL,
    chulo character varying NOT NULL,
    tipo character varying,
    nombre character varying,
    fecha_inicio character varying,
    fecha_fin character varying
);


ALTER TABLE public.proyectos OWNER TO postgres;

--
-- Name: proyectos_ley; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.proyectos_ley (
    nro character varying NOT NULL,
    consecutivo integer NOT NULL,
    chulo character varying NOT NULL,
    nombre character varying,
    ambito character varying,
    pais character varying,
    ano integer,
    fecha date,
    objeto character varying,
    institucion character varying,
    autores character varying
);


ALTER TABLE public.proyectos_ley OWNER TO postgres;

--
-- Name: redes_conocimiento_especializado; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.redes_conocimiento_especializado (
    nro character varying,
    consecutivo integer NOT NULL,
    chulo character varying NOT NULL,
    nombre character varying,
    tipo character varying,
    ciudad character varying,
    fecha_inicio date,
    fecha_fin date,
    numero_participantes character varying
);


ALTER TABLE public.redes_conocimiento_especializado OWNER TO postgres;

--
-- Name: reglamentos_tecnicos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.reglamentos_tecnicos (
    nro character varying NOT NULL,
    consecutivo integer NOT NULL,
    chulo character varying NOT NULL,
    nombre character varying,
    disponibilidad character varying,
    pais character varying,
    ano integer,
    sitio_web character varying,
    institucion character varying,
    autores character varying
);


ALTER TABLE public.reglamentos_tecnicos OWNER TO postgres;

--
-- Name: regulaciones_normas; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.regulaciones_normas (
    nro character varying NOT NULL,
    tipo character varying NOT NULL,
    nombre character varying,
    chulo character varying NOT NULL,
    ambito character varying,
    pais character varying,
    ano integer,
    fecha date,
    objeto character varying,
    institucion character varying,
    autores character varying
);


ALTER TABLE public.regulaciones_normas OWNER TO postgres;

--
-- Name: signos_distintivos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.signos_distintivos (
    nro character varying NOT NULL,
    consecutivo integer NOT NULL,
    chulo character varying NOT NULL,
    nombre character varying,
    numero_registro character varying,
    pais character varying,
    ano integer,
    nombre_titular character varying
);


ALTER TABLE public.signos_distintivos OWNER TO postgres;

--
-- Name: softwares; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.softwares (
    nro character varying NOT NULL,
    consecutivo integer NOT NULL,
    chulo character varying NOT NULL,
    tipo character varying,
    titulo character varying,
    pais character varying,
    ano integer,
    disponibilidad character varying,
    sitio_web character varying NOT NULL,
    nombre_comercial character varying,
    nombre_proyecto character varying,
    institucion_financiadora character varying NOT NULL,
    autores character varying
);


ALTER TABLE public.softwares OWNER TO postgres;

--
-- Name: tablas_sin_seguimiento; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tablas_sin_seguimiento (
    nro character varying,
    table_title character varying,
    body character varying
);


ALTER TABLE public.tablas_sin_seguimiento OWNER TO postgres;

--
-- Name: talleres_creacion; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.talleres_creacion (
    nro character varying,
    nombre character varying,
    tipo_taller character varying,
    participacion character varying,
    fecha_inicio date,
    fecha_fin date,
    lugar_realizacion character varying,
    ambito character varying,
    distincion character varying,
    mecanismo_seleccions character varying
);


ALTER TABLE public.talleres_creacion OWNER TO postgres;

--
-- Name: trabajos_dirigidos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.trabajos_dirigidos (
    nro character varying,
    consecutivo integer NOT NULL,
    chulo character varying NOT NULL,
    nombre character varying,
    tipo character varying,
    ano_inicio integer,
    ano_fin integer,
    tipo_orientacion character varying,
    estudiante character varying,
    programa character varying,
    paginas character varying,
    valoracion character varying,
    institucion character varying,
    autores character varying
);


ALTER TABLE public.trabajos_dirigidos OWNER TO postgres;

--
-- Name: traducciones; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.traducciones (
    nro character varying NOT NULL,
    tipo character varying,
    titulo character varying,
    ano integer,
    revista character varying,
    libro character varying,
    medio_divulgacion character varying,
    idioma_original character varying,
    idioma_traduccion character varying,
    edicion character varying,
    serie character varying,
    autor_original character varying,
    autores character varying
);


ALTER TABLE public.traducciones OWNER TO postgres;

--
-- Name: datos_basicos PK_datos_basicos; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.datos_basicos
    ADD CONSTRAINT "PK_datos_basicos" PRIMARY KEY (nro);


--
-- Name: instituciones nro; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.instituciones
    ADD CONSTRAINT nro FOREIGN KEY (nro) REFERENCES public.datos_basicos(nro) ON DELETE CASCADE;


--
-- Name: plan_estrategico nro; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.plan_estrategico
    ADD CONSTRAINT nro FOREIGN KEY (nro) REFERENCES public.datos_basicos(nro) ON DELETE CASCADE;


--
-- Name: lineas_investigacion nro; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.lineas_investigacion
    ADD CONSTRAINT nro FOREIGN KEY (nro) REFERENCES public.datos_basicos(nro) ON DELETE CASCADE;


--
-- Name: integrantes nro; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.integrantes
    ADD CONSTRAINT nro FOREIGN KEY (nro) REFERENCES public.datos_basicos(nro) ON DELETE CASCADE;


--
-- Name: programas_doctorado nro; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.programas_doctorado
    ADD CONSTRAINT nro FOREIGN KEY (nro) REFERENCES public.datos_basicos(nro) ON DELETE CASCADE;


--
-- Name: programas_maestria nro; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.programas_maestria
    ADD CONSTRAINT nro FOREIGN KEY (nro) REFERENCES public.datos_basicos(nro) ON DELETE CASCADE;


--
-- Name: otros_programas_academicos nro; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.otros_programas_academicos
    ADD CONSTRAINT nro FOREIGN KEY (nro) REFERENCES public.datos_basicos(nro) ON DELETE CASCADE;


--
-- Name: curso_doctorado nro; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.curso_doctorado
    ADD CONSTRAINT nro FOREIGN KEY (nro) REFERENCES public.datos_basicos(nro) ON DELETE CASCADE;


--
-- Name: curso_maestria nro; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.curso_maestria
    ADD CONSTRAINT nro FOREIGN KEY (nro) REFERENCES public.datos_basicos(nro) ON DELETE CASCADE;


--
-- Name: curso_corta_duracion nro; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.curso_corta_duracion
    ADD CONSTRAINT nro FOREIGN KEY (nro) REFERENCES public.datos_basicos(nro) ON DELETE CASCADE;


--
-- Name: cursos_especializados_extension nro; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cursos_especializados_extension
    ADD CONSTRAINT nro FOREIGN KEY (nro) REFERENCES public.datos_basicos(nro) ON DELETE CASCADE;


--
-- Name: articulos_publicados nro; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.articulos_publicados
    ADD CONSTRAINT nro FOREIGN KEY (nro) REFERENCES public.datos_basicos(nro) ON DELETE CASCADE;


--
-- Name: libros_publicados nro; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.libros_publicados
    ADD CONSTRAINT nro FOREIGN KEY (nro) REFERENCES public.datos_basicos(nro) ON DELETE CASCADE;


--
-- Name: capitulos_libro nro; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.capitulos_libro
    ADD CONSTRAINT nro FOREIGN KEY (nro) REFERENCES public.datos_basicos(nro) ON DELETE CASCADE;


--
-- Name: documentos_trabajo nro; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.documentos_trabajo
    ADD CONSTRAINT nro FOREIGN KEY (nro) REFERENCES public.datos_basicos(nro) ON DELETE CASCADE;


--
-- Name: otra_pubicacion_divulgativa nro; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.otra_pubicacion_divulgativa
    ADD CONSTRAINT nro FOREIGN KEY (nro) REFERENCES public.datos_basicos(nro) ON DELETE CASCADE;


--
-- Name: traducciones nro; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.traducciones
    ADD CONSTRAINT nro FOREIGN KEY (nro) REFERENCES public.datos_basicos(nro) ON DELETE CASCADE;


--
-- Name: cartas_mapas nro; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cartas_mapas
    ADD CONSTRAINT nro FOREIGN KEY (nro) REFERENCES public.datos_basicos(nro) ON DELETE CASCADE;


--
-- Name: conceptos_tecnicos nro; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.conceptos_tecnicos
    ADD CONSTRAINT nro FOREIGN KEY (nro) REFERENCES public.datos_basicos(nro) ON DELETE CASCADE;


--
-- Name: disenos_industriales nro; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.disenos_industriales
    ADD CONSTRAINT nro FOREIGN KEY (nro) REFERENCES public.datos_basicos(nro) ON DELETE CASCADE;


--
-- Name: informes_tecnicos nro; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.informes_tecnicos
    ADD CONSTRAINT nro FOREIGN KEY (nro) REFERENCES public.datos_basicos(nro) ON DELETE CASCADE;


--
-- Name: innovaciones_procesos nro; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.innovaciones_procesos
    ADD CONSTRAINT nro FOREIGN KEY (nro) REFERENCES public.datos_basicos(nro) ON DELETE CASCADE;


--
-- Name: nuevas_variedades nro; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.nuevas_variedades
    ADD CONSTRAINT nro FOREIGN KEY (nro) REFERENCES public.datos_basicos(nro) ON DELETE CASCADE;


--
-- Name: plantas_piloto nro; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.plantas_piloto
    ADD CONSTRAINT nro FOREIGN KEY (nro) REFERENCES public.datos_basicos(nro) ON DELETE CASCADE;


--
-- Name: otros_productos_tec nro; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.otros_productos_tec
    ADD CONSTRAINT nro FOREIGN KEY (nro) REFERENCES public.datos_basicos(nro) ON DELETE CASCADE;


--
-- Name: prototipos nro; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.prototipos
    ADD CONSTRAINT nro FOREIGN KEY (nro) REFERENCES public.datos_basicos(nro) ON DELETE CASCADE;


--
-- Name: regulaciones_normas nro; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.regulaciones_normas
    ADD CONSTRAINT nro FOREIGN KEY (nro) REFERENCES public.datos_basicos(nro) ON DELETE CASCADE;


--
-- Name: reglamentos_tecnicos nro; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reglamentos_tecnicos
    ADD CONSTRAINT nro FOREIGN KEY (nro) REFERENCES public.datos_basicos(nro) ON DELETE CASCADE;


--
-- Name: proyectos_ley nro; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.proyectos_ley
    ADD CONSTRAINT nro FOREIGN KEY (nro) REFERENCES public.datos_basicos(nro) ON DELETE CASCADE;


--
-- Name: signos_distintivos nro; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.signos_distintivos
    ADD CONSTRAINT nro FOREIGN KEY (nro) REFERENCES public.datos_basicos(nro) ON DELETE CASCADE;


--
-- Name: softwares nro; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.softwares
    ADD CONSTRAINT nro FOREIGN KEY (nro) REFERENCES public.datos_basicos(nro) ON DELETE CASCADE;


--
-- Name: empresas_base_tecnologica nro; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.empresas_base_tecnologica
    ADD CONSTRAINT nro FOREIGN KEY (nro) REFERENCES public.datos_basicos(nro) ON DELETE CASCADE;


--
-- Name: consultorias_cientificas nro; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.consultorias_cientificas
    ADD CONSTRAINT nro FOREIGN KEY (nro) REFERENCES public.datos_basicos(nro) ON DELETE CASCADE;


--
-- Name: ediciones nro; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ediciones
    ADD CONSTRAINT nro FOREIGN KEY (nro) REFERENCES public.datos_basicos(nro) ON DELETE CASCADE;


--
-- Name: eventos_cientificos nro; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.eventos_cientificos
    ADD CONSTRAINT nro FOREIGN KEY (nro) REFERENCES public.datos_basicos(nro) ON DELETE CASCADE;


--
-- Name: informes_investigacion nro; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.informes_investigacion
    ADD CONSTRAINT nro FOREIGN KEY (nro) REFERENCES public.datos_basicos(nro) ON DELETE CASCADE;


--
-- Name: nuevas_secuencias_geneticas nro; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.nuevas_secuencias_geneticas
    ADD CONSTRAINT nro FOREIGN KEY (nro) REFERENCES public.datos_basicos(nro) ON DELETE CASCADE;


--
-- Name: redes_conocimiento_especializado nro; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.redes_conocimiento_especializado
    ADD CONSTRAINT nro FOREIGN KEY (nro) REFERENCES public.datos_basicos(nro) ON DELETE CASCADE;


--
-- Name: generaciones_contenido_audio nro; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.generaciones_contenido_audio
    ADD CONSTRAINT nro FOREIGN KEY (nro) REFERENCES public.datos_basicos(nro) ON DELETE CASCADE;


--
-- Name: generaciones_contenido_impreso nro; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.generaciones_contenido_impreso
    ADD CONSTRAINT nro FOREIGN KEY (nro) REFERENCES public.datos_basicos(nro) ON DELETE CASCADE;


--
-- Name: generaciones_contenido_multimedia nro; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.generaciones_contenido_multimedia
    ADD CONSTRAINT nro FOREIGN KEY (nro) REFERENCES public.datos_basicos(nro) ON DELETE CASCADE;


--
-- Name: generaciones_contenido_virtual nro; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.generaciones_contenido_virtual
    ADD CONSTRAINT nro FOREIGN KEY (nro) REFERENCES public.datos_basicos(nro) ON DELETE CASCADE;


--
-- Name: estrategias_comunicacion_conocimiento nro; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.estrategias_comunicacion_conocimiento
    ADD CONSTRAINT nro FOREIGN KEY (nro) REFERENCES public.datos_basicos(nro) ON DELETE CASCADE;


--
-- Name: estrategias_pedagogicas nro; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.estrategias_pedagogicas
    ADD CONSTRAINT nro FOREIGN KEY (nro) REFERENCES public.datos_basicos(nro) ON DELETE CASCADE;


--
-- Name: espacios_participacion_ciudadana nro; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.espacios_participacion_ciudadana
    ADD CONSTRAINT nro FOREIGN KEY (nro) REFERENCES public.datos_basicos(nro) ON DELETE CASCADE;


--
-- Name: participacion_cti nro; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.participacion_cti
    ADD CONSTRAINT nro FOREIGN KEY (nro) REFERENCES public.datos_basicos(nro) ON DELETE CASCADE;


--
-- Name: obras_productos nro; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.obras_productos
    ADD CONSTRAINT nro FOREIGN KEY (nro) REFERENCES public.datos_basicos(nro) ON DELETE CASCADE;


--
-- Name: industrias_creativas_culturales nro; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.industrias_creativas_culturales
    ADD CONSTRAINT nro FOREIGN KEY (nro) REFERENCES public.datos_basicos(nro) ON DELETE CASCADE;


--
-- Name: eventos_artisticos nro; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.eventos_artisticos
    ADD CONSTRAINT nro FOREIGN KEY (nro) REFERENCES public.datos_basicos(nro) ON DELETE CASCADE;


--
-- Name: talleres_creacion nro; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.talleres_creacion
    ADD CONSTRAINT nro FOREIGN KEY (nro) REFERENCES public.datos_basicos(nro) ON DELETE CASCADE;


--
-- Name: trabajos_dirigidos nro; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trabajos_dirigidos
    ADD CONSTRAINT nro FOREIGN KEY (nro) REFERENCES public.datos_basicos(nro) ON DELETE CASCADE;


--
-- Name: jurados nro; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.jurados
    ADD CONSTRAINT nro FOREIGN KEY (nro) REFERENCES public.datos_basicos(nro) ON DELETE CASCADE;


--
-- Name: participacion_comites nro; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.participacion_comites
    ADD CONSTRAINT nro FOREIGN KEY (nro) REFERENCES public.datos_basicos(nro) ON DELETE CASCADE;


--
-- Name: proyectos nro; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.proyectos
    ADD CONSTRAINT nro FOREIGN KEY (nro) REFERENCES public.datos_basicos(nro) ON DELETE CASCADE;


--
-- Name: demas_trabajos nro; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.demas_trabajos
    ADD CONSTRAINT nro FOREIGN KEY (nro) REFERENCES public.datos_basicos(nro) ON DELETE CASCADE;


--
-- Name: tablas_sin_seguimiento nro; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tablas_sin_seguimiento
    ADD CONSTRAINT nro FOREIGN KEY (nro) REFERENCES public.datos_basicos(nro) ON DELETE CASCADE;


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE USAGE ON SCHEMA public FROM PUBLIC;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- Name: TABLE articulos_publicados; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.articulos_publicados TO dev_user;


--
-- Name: TABLE capitulos_libro; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.capitulos_libro TO dev_user;


--
-- Name: TABLE cartas_mapas; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.cartas_mapas TO dev_user;


--
-- Name: TABLE conceptos_tecnicos; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.conceptos_tecnicos TO dev_user;


--
-- Name: TABLE consultorias_cientificas; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.consultorias_cientificas TO dev_user;


--
-- Name: TABLE curso_corta_duracion; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.curso_corta_duracion TO dev_user;


--
-- Name: TABLE curso_doctorado; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.curso_doctorado TO dev_user;


--
-- Name: TABLE curso_maestria; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.curso_maestria TO dev_user;


--
-- Name: TABLE cursos_especializados_extension; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.cursos_especializados_extension TO dev_user;


--
-- Name: TABLE datos_basicos; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.datos_basicos TO dev_user;


--
-- Name: TABLE demas_trabajos; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.demas_trabajos TO dev_user;


--
-- Name: TABLE disenos_industriales; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.disenos_industriales TO dev_user;


--
-- Name: TABLE documentos_trabajo; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.documentos_trabajo TO dev_user;


--
-- Name: TABLE ediciones; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.ediciones TO dev_user;


--
-- Name: TABLE empresas_base_tecnologica; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.empresas_base_tecnologica TO dev_user;


--
-- Name: TABLE espacios_participacion_ciudadana; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.espacios_participacion_ciudadana TO dev_user;


--
-- Name: TABLE estrategias_comunicacion_conocimiento; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.estrategias_comunicacion_conocimiento TO dev_user;


--
-- Name: TABLE estrategias_pedagogicas; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.estrategias_pedagogicas TO dev_user;


--
-- Name: TABLE eventos_artisticos; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.eventos_artisticos TO dev_user;


--
-- Name: TABLE eventos_cientificos; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.eventos_cientificos TO dev_user;


--
-- Name: TABLE generaciones_contenido_audio; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.generaciones_contenido_audio TO dev_user;


--
-- Name: TABLE generaciones_contenido_impreso; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.generaciones_contenido_impreso TO dev_user;


--
-- Name: TABLE generaciones_contenido_multimedia; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.generaciones_contenido_multimedia TO dev_user;


--
-- Name: TABLE generaciones_contenido_virtual; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.generaciones_contenido_virtual TO dev_user;


--
-- Name: TABLE industrias_creativas_culturales; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.industrias_creativas_culturales TO dev_user;


--
-- Name: TABLE informes_investigacion; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.informes_investigacion TO dev_user;


--
-- Name: TABLE informes_tecnicos; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.informes_tecnicos TO dev_user;


--
-- Name: TABLE innovaciones_procesos; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.innovaciones_procesos TO dev_user;


--
-- Name: TABLE instituciones; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.instituciones TO dev_user;


--
-- Name: TABLE integrantes; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.integrantes TO dev_user;


--
-- Name: TABLE jurados; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.jurados TO dev_user;


--
-- Name: TABLE libros_publicados; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.libros_publicados TO dev_user;


--
-- Name: TABLE lineas_investigacion; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.lineas_investigacion TO dev_user;


--
-- Name: TABLE nuevas_secuencias_geneticas; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.nuevas_secuencias_geneticas TO dev_user;


--
-- Name: TABLE nuevas_variedades; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.nuevas_variedades TO dev_user;


--
-- Name: TABLE obras_productos; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.obras_productos TO dev_user;


--
-- Name: TABLE otra_pubicacion_divulgativa; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.otra_pubicacion_divulgativa TO dev_user;


--
-- Name: TABLE otros_productos_tec; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.otros_productos_tec TO dev_user;


--
-- Name: TABLE otros_programas_academicos; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.otros_programas_academicos TO dev_user;


--
-- Name: TABLE participacion_comites; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.participacion_comites TO dev_user;


--
-- Name: TABLE participacion_cti; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.participacion_cti TO dev_user;


--
-- Name: TABLE plan_estrategico; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.plan_estrategico TO dev_user;


--
-- Name: TABLE plantas_piloto; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.plantas_piloto TO dev_user;


--
-- Name: TABLE programas_doctorado; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.programas_doctorado TO dev_user;


--
-- Name: TABLE programas_maestria; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.programas_maestria TO dev_user;


--
-- Name: TABLE prototipos; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.prototipos TO dev_user;


--
-- Name: TABLE proyectos; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.proyectos TO dev_user;


--
-- Name: TABLE proyectos_ley; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.proyectos_ley TO dev_user;


--
-- Name: TABLE redes_conocimiento_especializado; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.redes_conocimiento_especializado TO dev_user;


--
-- Name: TABLE reglamentos_tecnicos; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.reglamentos_tecnicos TO dev_user;


--
-- Name: TABLE regulaciones_normas; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.regulaciones_normas TO dev_user;


--
-- Name: TABLE signos_distintivos; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.signos_distintivos TO dev_user;


--
-- Name: TABLE softwares; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.softwares TO dev_user;


--
-- Name: TABLE tablas_sin_seguimiento; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.tablas_sin_seguimiento TO dev_user;


--
-- Name: TABLE talleres_creacion; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.talleres_creacion TO dev_user;


--
-- Name: TABLE trabajos_dirigidos; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.trabajos_dirigidos TO dev_user;


--
-- Name: TABLE traducciones; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.traducciones TO dev_user;


--
-- PostgreSQL database dump complete
--

