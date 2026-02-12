document.addEventListener("DOMContentLoaded", function () {

    //------------------------------------------------------
    //--------- FORMATO DINERO PARA SALARIO BASICO ---------
    //------------------------------------------------------
    window.formatoMiles = function (valor) {
        valor = valor.replace(/[\D]/g, "");
        if (valor === '') return;

        return parseInt(valor, 10).toLocaleString('es-CO');
    }
    //------------------------------------------------------
    //--- MOSTAR Y OCULTAR DATOS DE FORM  NUEVO EMPLEADO ---
    //------------------------------------------------------
    const selectEstudia = document.getElementById('estudia_actualmente');
    const divEstudio = document.getElementById('estudio_actual');
    const inputEstudio = document.getElementById('nombre_programa_actual');

    if (selectEstudia && divEstudio) {
        selectEstudia.addEventListener('change', () => {
            if (selectEstudia.value === 'SI') {
                divEstudio.style.display = 'block';
            } else {
                divEstudio.style.display = 'none';
                divEstudio.querySelector('input').value = '';
                inputEstudio.value = 'N/A';
            }
        });
    }
    const $selectCiudad = $('#barrio'); // Select2 trabaja mejor con selectores de jQuery
    const divLocalidad = document.getElementById('localidad');
    const inputLocalidad = document.getElementById('localidad_id');

    if ($selectCiudad.length && divLocalidad) {
        // Select2 usa el evento 'select2:select' o simplemente 'change' pero disparado por el plugin
        $selectCiudad.on('change', function (e) {
            // Obtenemos el valor actual a través de jQuery/Select2
            const textoSeleccionado = $(this).find('option:selected').text();

            if (textoSeleccionado === 'D.C. - BOGOTÁ') {
                divLocalidad.style.display = 'block';
            } else {
                divLocalidad.style.display = 'none';

                // Limpiamos los inputs internos
                const innerInput = divLocalidad.querySelector('input');
                if (innerInput) innerInput.value = '';

                if (inputLocalidad) inputLocalidad.value = 'N/A';
            }
        });
    }

    //------------------------------------------------------
    //------------------ GENERA ANTIGUEDAD -----------------
    //------------------------------------------------------
    const fechaIngreso = document.getElementById('fecha_ingreso_antigua');
    const hoy = new Date()
    const inputAntiguedad = document.getElementById('antiguedad');

    window.calcularAntiguedad = function () {
        if (!fechaIngreso || !fechaIngreso.value) {
            inputAntiguedad.value = '';
            return;
        }
        const inicio = new Date(fechaIngreso.value);
        const fin = new Date(hoy);

        let antiguedad = fin.getFullYear() - inicio.getFullYear();

        const mesDif = fin.getMonth() - inicio.getMonth();
        const diaDif = fin.getDate() - inicio.getDate();

        //ajusta si aun no cumple el año
        if (mesDif < 0 || (mesDif === 0 && diaDif < 0)) {
            antiguedad--
        }
        inputAntiguedad.value = antiguedad
    }
    if (fechaIngreso) {
        fechaIngreso.addEventListener('change', calcularAntiguedad);
    }

    //------------------------------------------------------
    //-------------------- GENERA EDAD ---------------------
    //------------------------------------------------------
    const fechaNacimiento = document.getElementById('fecha_nacimiento');
    const inputEdad = document.getElementById('edad');

    if (fechaNacimiento && inputEdad) {
        window.calculaEdad = function () {
            if (!fechaNacimiento.value) {
                inputEdad.value = '';
                return;
            }
            const nacimiento = new Date(fechaNacimiento.value);
            const hoy = new Date()

            if (nacimiento > hoy) {
                alert('La fecha de nacimiento no puede ser mayor a hoy');
                return;
            }
            let edad = hoy.getFullYear() - nacimiento.getFullYear();
            const mesDiff = hoy.getMonth() - nacimiento.getMonth();
            const diaDiff = hoy.getDate() - nacimiento.getDate();

            //ajusta si no ha cumplido años
            if (mesDiff < 0 || (mesDiff === 0 && diaDiff < 0)) {
                edad--;
            }
            inputEdad.value = edad;
        }
        fechaNacimiento.addEventListener('change', calculaEdad);
    }

    //------------------------------------------------------
    //------ WIZARD PARA MODAL DE FORM NUEVO EMPLEADO ------
    //------------------------------------------------------
    let currenStep = 0;
    const steps = document.querySelectorAll('.wizard-step');
    const btnGuardar = document.getElementById('btnGuardar');
    const btnSiguiente = document.getElementById('btnSiguiente');

    function showStep(index) {
        steps.forEach((step, i) => {
            step.classList.toggle('active', i === index);
        });
        if (btnGuardar && btnSiguiente) {
            btnGuardar.style.display = index == steps.length - 1 ? 'inline-block' : 'none';
            btnSiguiente.style.display = index == steps.length - 1 ? 'none' : 'inline-block';
        }
    }

    window.nextStep = function () {
        if (currenStep < steps.length - 1) {
            currenStep++;
            showStep(currenStep)
        }
    };
    window.prevStep = function () {
        if (currenStep > 0) {
            currenStep--;
            showStep(currenStep)
        }
    };
    window.abrirModalEmpleado = function () {
        currenStep = 0;
        showStep(currenStep);
        document.getElementById('modalEmpleado')?.classList.add('active');
    };
    window.cerrarModalEmpleado = function () {
        document.getElementById('modalEmpleado')?.classList.remove('active');
    };
    showStep(currenStep);

    //------------------------------------------------------
    //------------ SUBMIT DE FORM NUEVO EMPLEADO -----------
    //------------------------------------------------------
    const formEmpleado = document.getElementById('form_Empleado');
    if (formEmpleado) {
        formEmpleado.addEventListener('submit', function (e) {
            e.preventDefault();

            const form = this
            const data = new FormData(form);

            //detecta si es edicion
            const editId = form.dataset.editId;
            let url = '/rrhh/empleados/crear';
            if (editId) {
                url = `/rrhh/empleados/editar/${editId}`;
            }

            fetch(url, {
                method: 'POST',
                body: data
            })
                .then(res => res.json())
                .then(resp => {
                    if (!resp.success) {
                        alert(resp.error);
                        return;
                    }
                    resp.empleado.documentos_estudio = resp.documentos_estudio
                    if (editId) {
                        alert("Empleado Actualizadp");
                        window.actualizarFilaEmpleado(resp.empleado);
                    } else {
                        alert('Empleado Creado Correctamente');
                        window.agregarEmpleadoTabla(resp.empleado);
                    }
                    window.cerrarModalEmpleado();
                    form.reset();
                    delete form.dataset.editId;
                    document.getElementById("btnGuardar").textContent = "Guardar";
                })
                .catch(err => {
                    console.error(err);
                    alert('Error al crear empleado');
                });
        });
    }

    //------------------------------------------------------
    //--------- AGREGA FILAS A LA TABLA EMPLEADOS ----------
    //------------------------------------------------------
    window.agregarEmpleadoTabla = function (emp) {
        const tbody = document.getElementById('tabla_lista_empleados_body');
        const trPrincipal = document.createElement('tr');
        trPrincipal.classList.add('fila-principal');
        trPrincipal.dataset.id = emp.id;

        trPrincipal.innerHTML = `
            <td data-column="identificacion">${emp.identificacion}</td> <!-- tipo_documento -->
            <td data-column="nombres_y_apellidos">${emp.apellidos} ${emp.nombres}</td> <!-- consecutivo -->
            <td data-column="cargo">${emp.cargos}</td> <!-- nombre_documento -->
            <td data-column="tipo_contrato">${emp.tipo_contrato}</td> <!-- fecha_ultima_revision -->
            <td class="acciones">
                <button type="button" class="btn-accion btn-foto btn-preview"
                    data-url="${emp.cedula_path ? emp.cedula_path.replace(/\\\\/g, '/') : ''}" data-tipo="cedula"><i
                        class="fa-regular fa-id-card"></i></button>
                <button type="button" class="btn-accion btn-foto btn-preview"
                    data-url="${emp.foto_path ? emp.foto_path.replace(/\\\\/g, '/') : ''}" data-tipo="foto"><i
                        class="fa-solid fa-image-portrait"></i></button>
                <button type="button" class="btn-accion btn-editar" data-id="${emp.id}"><i class="fa-solid fa-user-pen"></i></button>
                <button type="button" class="btn-accion btn-eliminar" data-id="${emp.id}"><i class="fa-solid fa-person-circle-minus"></i></button>
            </td>
        `;

        const trDetalle = document.createElement('tr');
        trDetalle.classList.add('fila-detalles');
        trDetalle.style.display = 'none';
        trDetalle.innerHTML = `
            <td colspan="5">
        <div class="detalles-contenido">
                    <div class="detalle-item"><strong>Cedula Expedida en:</strong> <span
                            data-column="cedual_expedida_en">${emp.cedula_expedida_en}</span></div>
                    <div class="detalle-item"><strong>Sexo:</strong> <span data-column="sexo">${emp.sexo}</span>
                    </div>
                    <div class="detalle-item"><strong>Edad:</strong> <span data-column="cargo">${emp.edad}</span>
                    </div>
                    <div class="detalle-item"><strong>Fecha de Nacimiento:</strong> <span
                            data-column="fecha_nacimiento">${emp.fecha_nacimiento}</span></div>
                    <div class="detalle-item"><strong>Lugar de Nacimiento:</strong> <span
                            data-column="lugar_nacimiento">${emp.lugar_nacimiento}</span></div>
                    <div class="detalle-item"><strong>Edad:</strong> <span data-column="edad">${emp.edad}</span>
                    </div>
                    <div class="detalle-item"><strong>Estado Civil:</strong> <span data-column="estado_civil_id">${emp.estado_civil_id}</span></div>
                    <div class="detalle-item"><strong>Correo:</strong> <span data-column="correo">${emp.correo}</span></div>
                    <div class="detalle-item"><strong>Grupo Sanguineo RH:</strong> <span
                            data-column="grupo_sanguineo_id">${emp.gurpo_sanguineo_id}</span></div>
                    <div class="detalle-item"><strong>N° Hijos:</strong> <span data-column="numero_hijos">${emp.numero_hijos}</span></div>
                    <div class="detalle-item"><strong>Direccion:</strong> <span data-column="direccion">${emp.direccion}</span></div>
                    <div class="detalle-item"><strong>Barrio:</strong> <span data-column="barrio">${emp.barrio}</span></div>
                    <div class="detalle-item"><strong>Localidad:</strong> <span data-column="localidad">${emp.localidad}</span></div>
                    <div class="detalle-item"><strong>Estrato:</strong> <span data-column="estrato">${emp.estrato}</span></div>
                    <div class="detalle-item"><strong>Telefono Fijo:</strong> <span data-column="telefono_fijo">${emp.telefono_fijo}</span></div>
                    <div class="detalle-item"><strong>Celular:</strong> <span data-column="celular">${emp.celular}</span></div>
                    <div class="detalle-item"><strong>Contacto de Emergencia:</strong> <span
                            data-column="contacto_emergencia">${emp.contacto_emergencia}</span></div>
                    <div class="detalle-item"><strong>Telefono de Emergencia:</strong> <span
                            data-column="telefono_emergencia">${emp.telefono_emergencia}</span></div>
                    <div class="detalle-item"><strong>Parentesco:</strong> <span data-column="parentesco">${emp.parentesco}</span></div>
                    <div class="detalle-item"><strong>EPS:</strong> <span data-column="eps_id">${emp.eps_id}</span>
                    </div>
                    <div class="detalle-item"><strong>AFP:</strong> <span data-column="afp_id">${emp.afp_id}</span>
                    </div>
                    <div class="detalle-item"><strong>Cesantias:</strong> <span data-column="cesantias_id">${emp.cesantias_id}</span></div>
                    <div class="detalle-item"><strong>CCF:</strong> <span data-column="ccf_id">${emp.ccf_id}</span>
                    </div>
                    <div class="detalle-item"><strong>ARL:</strong> <span data-column="arl_id">${emp.arl_id}</span>
                    </div>
                    <div class="detalle-item"><strong>Jornada:</strong> <span data-column="jornada">${emp.jornada}</span></div>
                    <div class="detalle-item"><strong>Sede:</strong> <span data-column="sede">${emp.sedes}</span>
                    </div>
                    <div class="detalle-item"><strong>Antiguedad:</strong> <span data-column="antiguedad">${emp.antiguedad}</span></div>
                    <div class="detalle-item"><strong>Nivel de Escolaridad:</strong> <span
                            data-column="nivel_escolaridad_id">${emp.nivel_escolaridad_id}</span></div>
                    <div class="detalle-item"><strong>Programa Academico:</strong> <span
                            data-column="programa_academico">${emp.programa_academico}</span></div>
                    <div class="detalle-item"><strong>Estudia Actualmente:</strong> <span
                            data-column="estudia_actualmente">${emp.estudia_actualmente}</span></div>
                    <div class="detalle-item"><strong>Nombre del Programa Actual:</strong> <span
                            data-column="nombre_programa_actual">${emp.nombre_programa_actual}</span></div>
                    <div class="detalle-item"><strong>Salario Basico:</strong> <span data-column="salario_basico">${emp.salario_basico}</span></div>
                    <div class="detalle-item"><strong>Factor No Salarial:</strong> <span
                            data-column="factor_no_salarial">${emp.factor_no_salarial}</span></div>
                    <div class="detalle-item"><strong>N° Cuenta:</strong> <span data-column="numero_cuenta">${emp.numero_cuenta}</span></div>
                    <div class="detalle-item"><strong>Banco:</strong> <span data-column="banco">${emp.banco}</span>
                    </div>
                    <div class="detalle-item"><strong>Ver Documentos de Estudio:</strong> <span data-column="estudio">
                            <button type="button" class="btn-accion btn-docs" data-id="${emp.id}"><i
                                    class="fa-solid fa-folder-open"></i></button>
                        </span>
                    <div class="detalle-item"><strong>Cantidad de Contratos:</strong> <span
                            data-column="cantidad_contratos">
                            ${emp.cantidad_contratos}
                            <button type="button" class="btn-accion btn-contratos" data-id="${emp.id}"><i class="fa-solid fa-eye"></i></button>
                        </span>
                    </div>
                    <div class="detalle-item"><span data-column="genera_certificado">
                            <button type="button" class="btn-accion btn-certificado" data-id="${emp.id}"
                                title="Generar Certificado"><i class="fa-solid fa-file-pdf"></i> Genera Certificado</button>
                        </span>
                    </div>
                </div>
            </td>
        `;
        tbody.prepend(trDetalle);
        tbody.prepend(trPrincipal);

    }

    //------------------------------------------------------
    //-------------- EXPANDE FILAS DE LA TABLA -------------
    //------------------------------------------------------

    const tbody_detalles = document.getElementById('tabla_lista_empleados_body');
    if (tbody_detalles) {
        tbody_detalles.addEventListener('click', function (e) {
            const fila = e.target.closest('.fila-principal');
            if (!fila) return;

            if (e.target.closest('.acciones')) return;

            const filaDetalles_b = fila.nextElementSibling;
            if (!filaDetalles_b || !filaDetalles_b.classList.contains('fila-detalles')) return;

            tbody_detalles.querySelectorAll('.fila-detalles').forEach(det => {
                if (det !== filaDetalles_b) {
                    det.style.display = 'none';
                }
            });
            filaDetalles_b.style.display =
                filaDetalles_b.style.display === 'table-row' ? 'none' : 'table-row'
        });
    }

    //------------------------------------------------------
    //------------ BOTONES DE ACCION DOCUMENTOS ------------
    //------------------------------------------------------
    document.addEventListener('click', function (e) {
        const btnDocs = e.target.closest(".btn-docs");
        if (btnDocs) {
            e.preventDefault();
            e.stopPropagation();
            const empleadoId = btnDocs.dataset.id;
            cargarDocumentosEmpleado(empleadoId);
            return;
        }
        const btn = e.target.closest('.btn-preview');
        if (!btn) return;
        e.preventDefault();
        e.stopPropagation();
        abrirArchivo(btn.dataset.url)
    });

    window.abrirListaDocumentos = function (docs) {
        window.docActuales = docs;
        const modal = document.getElementById("modalPreview");
        const lista = document.getElementById("previewListaDocs");
        const img = document.getElementById("previewImg");
        const pdf = document.getElementById("previewPdf");

        img.style.display = 'none';
        pdf.style.display = 'none';
        lista.style.display = 'block';

        lista.innerHTML = "<h3>Documentos de estudio</h3>";
        if (docs.length === 0) {
            lista.innerHTML += "<p>No hay Documentos Cargados</p>";
        }
        docs.forEach((ruta, i) => {
            lista.innerHTML += `
                <div style="margin:10px 0;">
                    <button class="btn-doc-item"
                        onclick="abrirArchivo('${ruta}')">
                        Documento ${i + 1}
                    </button>
                    <br>
                </div>
            `;
        });
        document.getElementById("btnVolverLista").style.display = 'none';
        modal.classList.add("active")
    }
    window.abrirArchivo = function (url) {
        const modal = document.getElementById("modalPreview");
        const lista = document.getElementById("previewListaDocs");
        const img = document.getElementById("previewImg");
        const pdf = document.getElementById("previewPdf");
        document.getElementById("btnVolverLista").style.display = "inline-block";

        img.style.display = 'none';
        pdf.style.display = 'none';
        lista.style.display = 'none';

        if (url.match(/\.(jpg|jpeg|png|tiff)$/i)) {
            img.src = '/' + url;
            img.style.display = 'block';
        } else if (url.match(/\.pdf$/i)) {
            pdf.src = '/' + url;
            pdf.style.display = 'block';
        }
        modal.classList.add("active");
    }
    window.cerrarPreview = function () {
        const modal = document.getElementById('modalPreview');
        document.getElementById('previewImg').src = '';
        document.getElementById('previewPdf').src = '';
        modal.classList.remove('active');
    }
    window.cargarDocumentosEmpleado = function (id) {
        fetch(`/rrhh/empleados/${id}/documentos`)
            .then(res => res.json())
            .then(resp => {
                if (!resp.success) {
                    alert("Error Cargando documentos");
                    return;
                }
                abrirListaDocumentos(resp.documentos);
            })
            .catch(err => {
                console.error(err);
                alert("Error en servidor");
            });
    }

    window.volverListaDocs = function () {
        if (window.docActuales) {
            abrirListaDocumentos(window.docActuales);
        }
    }


    //------------------------------------------------------
    //--------------- MODAL EDITAR EMPLEADO ----------------
    //------------------------------------------------------
    document.addEventListener("click", function (e) {
        const btnEditar = e.target.closest(".btn-editar");
        if (btnEditar) {
            e.preventDefault();
            e.stopPropagation();

            const empleadoId = btnEditar.dataset.id;
            abrirModalEditarEmpleado(empleadoId);
            return
        }
    })
    window.abrirModalEditarEmpleado = function (id) {
        fetch(`/rrhh/empleados/${id}/json`)
            .then(res => res.json())
            .then(resp => {
                if (!resp.success) {
                    alert("No se pudo cargar el empleado");
                    return;
                }
                const emp = resp.empleado

                document.getElementById("identificacion").value = emp.identificacion;
                document.getElementById("nombres").value = emp.nombres;
                document.getElementById("apellidos").value = emp.apellidos;
                document.getElementById("cedula_expedida_en").value = emp.cedula_expedida_en;
                document.getElementById("sexo").value = emp.sexo;
                document.getElementById("fecha_nacimiento").value = emp.fecha_nacimiento;
                document.getElementById("lugar_nacimiento").value = emp.lugar_nacimiento;
                document.getElementById("edad").value = emp.edad;
                document.getElementById("estado_civil_id").value = emp.estado_civil_id;
                document.getElementById("grupo_sanguineo_id").value = emp.grupo_sanguineo_id;
                document.getElementById("numero_hijos").value = emp.numero_hijos;
                document.getElementById("direccion").value = emp.direccion;
                $("#barrio").val(emp.barrio_id).trigger("change");
                document.getElementById("localidad").value = emp.localidad;
                document.getElementById("estrato").value = emp.estrato;
                document.getElementById("telefono_fijo").value = emp.telefono_fijo;
                document.getElementById("celular").value = emp.celular;
                document.getElementById("correo").value = emp.correo;
                document.getElementById("contacto_emergencia").value = emp.contacto_emergencia;
                document.getElementById("telefono_emergencia").value = emp.telefono_emergencia;
                document.getElementById("parentesco").value = emp.parentesco;
                document.getElementById("eps_id").value = emp.eps_id;
                document.getElementById("afp_id").value = emp.afp_id;
                document.getElementById("cesantias_id").value = emp.cesantias_id;
                document.getElementById("ccf_id").value = emp.ccf_id;
                document.getElementById("arl_id").value = emp.arl_id;
                document.getElementById("fecha_ingreso_antigua").value = emp.fecha_ingreso;
                document.getElementById("tipo_contrato_id").value = emp.tipo_contrato_id;
                document.getElementById("cargo_id").value = emp.cargo_id;
                document.getElementById("jornada").value = emp.jornada;
                document.getElementById("sede").value = emp.sede;
                document.getElementById("antiguedad").value = emp.antiguedad;
                document.getElementById("salario_basico").value = emp.salario_basico;
                document.getElementById("factor_no_salarial").value = emp.factor_no_salarial;
                document.getElementById("numero_cuenta").value = emp.numero_cuenta;
                document.getElementById("banco").value = emp.banco;
                document.getElementById("grupo_nomina_id").value = emp.grupo_nomina_id;
                document.getElementById("nivel_escolaridad_id").value = emp.nivel_escolaridad_id;
                document.getElementById("programa_academico").value = emp.programa_academico;
                document.getElementById("estudia_actualmente").value = emp.estudia_actualmente;
                document.getElementById("nombre_programa_actual").value = emp.nombre_programa_actual;

                document.getElementById("form_Empleado").dataset.editId = id;

                document.getElementById("btnGuardar").textContent = "Actualizar";

                abrirModalEmpleado();
            })
            .catch(err => {
                console.error(err);
                alert("Error cargando empleado");
            });
    };

    window.actualizarFilaEmpleado = function (emp) {
        const filaPrincipal = document.querySelector(`.fila-principal[data-id="${emp.id}"]`);

        if (!filaPrincipal) return;

        filaPrincipal.querySelector('[data-column="identificacion"]').textContent = emp.identificacion;
        filaPrincipal.querySelector('[data-column="nombres_y_apellidos"]').textContent = emp.apellidos + " " + emp.nombres;
        filaPrincipal.querySelector('[data-column="correo"]').textContent = emp.correo;
        filaPrincipal.querySelector('[data-column="cargo_id"]').textContent = emp.cargo_id;
        filaPrincipal.querySelector('[data-column="tipo_contrato_id"]').textContent = emp.tipo_contrato_id;

        const filaDetalles = filaPrincipal.nextElementSibling;
        if (filaDetalles && filaDetalles.classList.contains('fila-detalles')) {
            filaDetalles.querySelector('[data-column="cedula_expedida_en"]').textContent = emp.cedula_expedida_en;
            filaDetalles.querySelector('[data-column="sexo"]').textContent = emp.sexo;
            filaDetalles.querySelector('[data-column="fecha_nacimiento"]').textContent = emp.fecha_nacimiento;
            filaDetalles.querySelector('[data-column="lugar_nacimiento"]').textContent = emp.lugar_nacimiento;
            filaDetalles.querySelector('[data-column="edad"]').textContent = emp.edad;
            filaDetalles.querySelector('[data-column="estado_civil_id"]').textContent = emp.estado_civil_id;
            filaDetalles.querySelector('[data-column="grupo_sanguineo_id"]').textContent = emp.grupo_sanguineo_id;
            filaDetalles.querySelector('[data-column="numero_hijos"]').textContent = emp.numero_hijos;
            filaDetalles.querySelector('[data-column="direccion"]').textContent = emp.direccion;
            filaDetalles.querySelector('[data-column="barrio"]').textContent = emp.barrio;
            filaDetalles.querySelector('[data-column="localidad"]').textContent = emp.localidad;
            filaDetalles.querySelector('[data-column="estrato"]').textContent = emp.estrato;
            filaDetalles.querySelector('[data-column="telefono_fijo"]').textContent = emp.telefono_fijo;
            filaDetalles.querySelector('[data-column="celular"]').textContent = emp.celular;
            filaDetalles.querySelector('[data-column="contacto_emergencia"]').textContent = emp.contacto_emergencia;
            filaDetalles.querySelector('[data-column="telefono_emergencia"]').textContent = emp.telefono_emergencia;
            filaDetalles.querySelector('[data-column="parentesco"]').textContent = emp.parentesco;
            filaDetalles.querySelector('[data-column="eps_id"]').textContent = emp.eps_id;
            filaDetalles.querySelector('[data-column="afp_id"]').textContent = emp.afp_id;
            filaDetalles.querySelector('[data-column="cesantias_id"]').textContent = emp.cesantias_id;
            filaDetalles.querySelector('[data-column="ccf_id"]').textContent = emp.ccf_id;
            filaDetalles.querySelector('[data-column="arl_id"]').textContent = emp.arl_id;
            filaDetalles.querySelector('[data-column="jornada"]').textContent = emp.jornada;
            filaDetalles.querySelector('[data-column="sede"]').textContent = emp.sede;
            filaDetalles.querySelector('[data-column="fecha_ingreso_antigua"]').textContent = emp.fecha_ingreso;
            filaDetalles.querySelector('[data-column="antiguedad"]').textContent = emp.antiguedad;
            filaDetalles.querySelector('[data-column="salario_basico"]').textContent = emp.salario_basico;
            filaDetalles.querySelector('[data-column="factor_no_salarial"]').textContent = emp.factor_no_salarial;
            filaDetalles.querySelector('[data-column="numero_cuenta"]').textContent = emp.numero_cuenta;
            filaDetalles.querySelector('[data-column="banco"]').textContent = emp.banco;
            filaDetalles.querySelector('[data-column="grupo_nomina_id"]').textContent = emp.grupo_nomina_id;
            filaDetalles.querySelector('[data-column="nivel_escolaridad_id"]').textContent = emp.nivel_escolaridad_id;
            filaDetalles.querySelector('[data-column="programa_academico"]').textContent = emp.programa_academico;
            filaDetalles.querySelector('[data-column="estudia_actualmente"]').textContent = emp.estudia_actualmente;
            filaDetalles.querySelector('[data-column="nombre_programa_actual"]').textContent = emp.nombre_programa_actual;
        }
    };

    //------------------------------------------------------
    //----------------- DESACTIVAR EMPLEADO ----------------
    //------------------------------------------------------
    let empleadoRetiroId = null;
    document.addEventListener("click", function (e) {
        const btnEliminar = e.target.closest(".btn-eliminar");
        if (!btnEliminar) return;
        e.preventDefault();
        e.stopPropagation();
        empleadoRetiroId = btnEliminar.dataset.id;
        document.getElementById("fecha_retiro").value = "";
        document.getElementById("modalRetiro").classList.add("active");
    });
    window.guardarFechaRetiro = function () {
        const motivoRetiro = document.getElementById("motivo_retiro").value;
        if (!motivoRetiro) {
            alert("Por favor ingrese un motivo de retiro");
            return;
        }
        const fechaRetiro = document.getElementById("fecha_retiro").value;
        if (!fechaRetiro) {
            alert("Por favor ingrese una fecha de retiro");
            return;
        }
        fetch(`/rrhh/empleados/retirar/${empleadoRetiroId}`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ fecha_retiro: fechaRetiro, motivo_retiro: motivoRetiro })
        })
            .then(res => res.json())
            .then(resp => {
                if (!resp.success) {
                    alert("error:" + resp.error);
                    return;
                }
                alert("Empleado retirado correctamente");
                document.getElementById("modalRetiro").classList.remove("active");
                location.reload();
            })
            .catch(err => {
                console.error(err);
                alert("Error en el servidor");
            });
    }

    window.cerrarModalRetiro = function () {
        const modal = document.getElementById('modalRetiro');
        modal.classList.remove('active');
    }

    //------------------------------------------------------
    //------------------ ACTIVAR EMPLEADO ------------------
    //------------------------------------------------------
    let empleadoActivarId = null;
    document.addEventListener("click", function (e) {
        const btnActivar = e.target.closest(".btn-activar");
        if (!btnActivar) return;
        e.preventDefault();
        e.stopPropagation();
        empleadoActivarId = btnActivar.dataset.id;
        document.getElementById("fecha_ingreso").value = "";
        document.getElementById("modalIngreso").classList.add("active");
    });
    window.guardarFechaIngreso = function () {
        const fechaIngreso = document.getElementById("fecha_ingreso").value;
        const salario_basico = document.getElementById("salario_basico_ingreso").value;
        const factor_no_salarial = document.getElementById("factor_no_salarial_ingreso").value;
        const tipoContrato = document.getElementById('tipo_contrato').value;
        if (!salario_basico) {
            alert("Por favor ingrese un salario basico");
            return;
        }
        if (!factor_no_salarial) {
            alert("Por favor ingrese un factor no salarial");
            return;
        }
        if (!fechaIngreso) {
            alert("Por favor ingrese una fecha de ingreso");
            return;
        }
        fetch(`/rrhh/empleados/activar/${empleadoActivarId}`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ fecha_ingreso: fechaIngreso, salario_basico: salario_basico, factor_no_salarial: factor_no_salarial, tipo_contrato: tipoContrato })
        })
            .then(res => res.json())
            .then(resp => {
                if (!resp.success) {
                    alert("error:" + resp.error);
                    return;
                }
                alert("Empleado activado correctamente");
                document.getElementById("modalIngreso").classList.remove("active");
                location.reload();
            })
            .catch(err => {
                console.error(err);
                alert("Error en el servidor");
            });
    }

    window.cerrarModalIngreso = function () {
        const modal = document.getElementById('modalIngreso');
        modal.classList.remove('active');
    }


    //------------------------------------------------------
    //---------- SELECT2 PARA BUSQUEDA DE CIUDADES ---------
    //------------------------------------------------------
    $(document).ready(function () {
        $('.select2_barrio').select2({
            placeholder: 'Buscar...',
            allowClear: true,
            width: '100%',
            dropdownParent: $('#modalEmpleado')
        });
    });


    const inputSalario = document.getElementById('salario_basico');
    const factor_no_salarial = document.getElementById("factor_no_salarial");
    const salario_ingreso = document.getElementById('salario_basico_ingreso');
    const factor_ingreso = document.getElementById("factor_no_salarial_ingreso");
    if (salario_ingreso) {
        salario_ingreso.addEventListener('input', function (e) {
            let cursorPos = this.selectionStart;
            let valorFormateado = formatoMiles(this.value);
            this.value = valorFormateado;
            this.setSelectionRange(this.value.length, this.value.length);
        });
    }
    if (factor_ingreso) {
        factor_ingreso.addEventListener('input', function (e) {
            let cursorPos = this.selectionStart;
            let valorFormateado = formatoMiles(this.value);
            this.value = valorFormateado;
            this.setSelectionRange(this.value.length, this.value.length);
        });
    }
    if (inputSalario) {
        inputSalario.addEventListener('input', function (e) {
            let cursorPos = this.selectionStart;
            let valorFormateado = formatoMiles(this.value);
            this.value = valorFormateado;
            this.setSelectionRange(this.value.length, this.value.length);
        });
    }
    if (factor_no_salarial) {
        factor_no_salarial.addEventListener('input', function (e) {
            let cursorPos = this.selectionStart;
            let valorFormateado = formatoMiles(this.value);
            this.value = valorFormateado;
            this.setSelectionRange(this.value.length, this.value.length);
        });
    }


    //------------------------------------------------------
    //--------- MODAL CONTRATOS ---------
    //------------------------------------------------------
    document.addEventListener('click', function (e) {
        const btnContratos = e.target.closest('.btn-contratos');
        if (btnContratos) {
            e.preventDefault();
            e.stopPropagation();
            const empleadoId = btnContratos.dataset.id;
            document.getElementById('modalContratos').classList.add('active');
            fetch(`/rrhh/empleados/${empleadoId}/contratos`)
                .then(res => res.json())
                .then(resp => {
                    if (!resp.success) {
                        alert('Error cargando contratos');
                        return;
                    }
                    const tbody = document.getElementById('tabla_contratos_empleado_body');
                    tbody.innerHTML = '';
                    resp.contratos.forEach(contrato => {

                        //crea fila princial
                        const trPrincipal = document.createElement('tr');
                        trPrincipal.classList.add('fila-principal-contrato');
                        
                        const tfin = (contrato.fecha_finalizacion === null || contrato.fecha_finalizacion === '')
                                ? 'Activo' : contrato.fecha_finalizacion;
                        const motivo = contrato.motivo || 'N/A';
                        trPrincipal.innerHTML = `
                                <td data-column="tipo_contrato">${contrato.tipo_contrato}</td>
                                <td data-column="fecha_inicio">${contrato.fecha_ingreso}</td>
                                <td data-column="fecha_fin">${tfin}</td>
                                <td data-column="salario_basico">$ ${contrato.salario_basico}</td>
                                <td data-column="factor_no_salarial">$ ${contrato.factor_no_salarial}</td>
                                <td data-column="motivo">${motivo}</td>
                                <td data-column="codigo_contrato">${contrato.n_consecutivo}</td>
                            `;
                        tbody.appendChild(trPrincipal);

                        //crea fila detalles (otrosi)
                        const trDetalle = document.createElement('tr');
                        trDetalle.classList.add('fila-detalles-contrato');
                        trDetalle.style.display = 'none';

                        let otrosiHTML = '';
                        if(contrato.otrosi && contrato.otrosi.length > 0){
                            otrosiHTML = `
                                <div class="otrosi-container">
                                    <h4> Otrosí realizados a este contrato:</h4>
                                    <table class="tabla-otrosi">
                                        <thead>
                                            <tr>
                                                <th>Tipo</th>
                                                <th>Fecha de Aplicacion</th>
                                                <th>Descripcion</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            ${contrato.otrosi.map(o => `
                                                <tr>
                                                    <td>${o.tipo_otrosi}</td>
                                                    <td>${o.fecha_inicio}</td>
                                                    <td>${o.descripcion}</td>
                                                </tr>
                                            `).join('')}
                                        </tbdoy>
                                    </table>
                                </div>
                            `;
                        } else {
                            otrosiHTML = `<p class="no-data">Este Contrato no tiene Otrosí registrados.</p>`;
                        }
                        trDetalle.innerHTML = `<td colspan="7">${otrosiHTML}</td>`;
                        tbody.appendChild(trDetalle);
                    });
                })
                .catch(err => {
                    alert('Error en el servidor');
                });
        }
    });
    window.cerrarModalContratos = function () {
        const modal = document.getElementById('modalContratos');
        modal.classList.remove('active');
    }

    //////logica de expansion de detalles contrato
    const tbodyContratos = document.getElementById('tabla_contratos_empleado_body');
    if(tbodyContratos){
        tbodyContratos.addEventListener('click', function(e){
            const fila = e.target.closest('.fila-principal-contrato');
            if(!fila) return;

            const filaDetalles = fila.nextElementSibling;
            if(!filaDetalles || !filaDetalles.classList.contains('fila-detalles-contrato')) return;

            const estaAbierta = filaDetalles.style.display === 'table-row';

            tbodyContratos.querySelectorAll('.fila-detalles-contrato').forEach(det => det.style.display = 'none');

            filaDetalles.style.display = estaAbierta ? 'none' : 'table-row';

            tbodyContratos.querySelectorAll('.fila-principal-contrato').forEach(f => f.classList.remove('seleccionada'));
            if(!estaAbierta) fila.classList.add('seleccionada');
        });
    }

    //------------------------------------------------------
    //--------- MODAL ACCIONES MASIVAS ---------
    //------------------------------------------------------
    let modoModal = 'crear';
    window.abrirModalImportar = function (modo) {
        modoModal = modo || 'crear';
        const modal = document.getElementById('modalImportar');
        const titulo = modal.querySelector('h3');
        titulo.textContent = modoModal === 'actualizar' ? 'Actualizar Empleados Masivamente' : 'Cargar Empleados Masivamente';
        modal.classList.add('active');
    };

    window.cerrarModalImportar = function () {
        document.getElementById('modalImportar').classList.remove('active');
        // Limpia el formulario y el mensaje al cerrar
        document.getElementById('formImportarExcel').reset();
        const res = document.getElementById('resultadoImportacion');
        res.style.display = 'none';
        res.innerHTML = '';
    };

    const formImportar = document.getElementById('formImportarExcel');

    if (formImportar) {
        formImportar.addEventListener('submit', function (e) {
            e.preventDefault(); // Evita que la página se recargue
            const endpoint = modoModal === 'crear'
                ? '/rrhh/empleados/importar_empleados'
                : '/rrhh/empleados/actualizar_empleados';
            const fileInput = document.getElementById('archivo_excel');
            const btnCargar = document.getElementById('btnCargarExcel');
            const resultadoDiv = document.getElementById('resultadoImportacion');

            // 1. Validar que haya un archivo
            if (fileInput.files.length === 0) {
                alert("Por favor, seleccione un archivo Excel.");
                return;
            }

            // 2. Preparar los datos para el envío
            const formData = new FormData();
            formData.append('file', fileInput.files[0]);

            // 3. Estado visual de "Cargando"
            btnCargar.disabled = true;
            btnCargar.textContent = "Procesando... espere";
            resultadoDiv.style.display = 'block';
            resultadoDiv.style.backgroundColor = '#f8f9fa';
            resultadoDiv.innerHTML = "Subiendo archivo y analizando datos...";

            // 4. Enviar al servidor
            fetch(endpoint, {
                method: 'POST',
                body: formData
            })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        // Éxito: Mostrar mensaje verde y recargar
                        resultadoDiv.style.backgroundColor = '#d4edda';
                        resultadoDiv.style.color = '#155724';

                        const cantidad = data.insertados || data.actualizados || 0;
                        const accion = modoModal === 'crear' ? 'importado' : 'actualizado';
                        resultadoDiv.innerHTML = `✅ ¡Éxito! Se han ${accion} ${cantidad} empleados correctamente.`;

                        setTimeout(() => {
                            location.reload(); // Recarga la tabla para ver los nuevos empleados
                        }, 2000);

                    } else {
                        // Error: Mostrar mensaje rojo
                        btnCargar.disabled = false;
                        btnCargar.textContent = "Procesar Carga";
                        resultadoDiv.style.backgroundColor = '#f8d7da';
                        resultadoDiv.style.color = '#721c24';
                        resultadoDiv.innerHTML = `❌ Error: ${data.error}`;
                    }
                })
                .catch(err => {
                    console.error("Error en Fetch:", err);
                    btnCargar.disabled = false;
                    btnCargar.textContent = "Procesar Carga";
                    alert("Ocurrió un error crítico al conectar con el servidor.");
                });
        });
    }

    //------------------------------------------------------
    //--------- ACCIONES MASIVAS PARA DOCUMENTOS ---------
    //------------------------------------------------------
    window.abrirModalZip = function () {
        document.getElementById('modalZip').classList.add('active');
    };

    window.cerrarModalZip = function () {
        document.getElementById('modalZip').classList.remove('active');
        document.getElementById('formImportarZip').reset();
    };

    document.getElementById('formImportarZip')?.addEventListener('submit', function (e) {
        e.preventDefault();
        const btn = document.getElementById('btnCargarZip');
        const resDiv = document.getElementById('resultadoZip');
        const formData = new FormData();
        formData.append('file', document.getElementById('archivo_zip').files[0]);

        btn.disabled = true;
        btn.textContent = "Procesando ZIP...";
        resDiv.style.display = 'block';
        resDiv.innerHTML = "Extrayendo y organizando archivos...";

        fetch('/rrhh/empleados/importar_zip', {
            method: 'POST',
            body: formData
        })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    alert(`¡Éxito! Se procesaron ${data.archivos} archivos.`);
                    location.reload();
                } else {
                    resDiv.innerHTML = `<span style="color:red">Error: ${data.error}</span>`;
                    btn.disabled = false;
                }
            });
    });

    //------------------------------------------------------
    //----------------------- BUSCAR -----------------------
    //------------------------------------------------------
    const inputBusqueda = document.getElementById('inputBusquedaID');
    if (inputBusqueda) {
        inputBusqueda.addEventListener('input', function () {
            const filtro = this.value.toLowerCase().trim();
            const tbody = document.getElementById('tabla_lista_empleados_body');
            const filasPrincipal = tbody.querySelectorAll('.fila-principal');

            filasPrincipal.forEach(filaPrincipal => {
                const celdaId = filaPrincipal.querySelector('[data-column="identificacion"]');
                const celdaNombre = filaPrincipal.querySelector('[data-column="nombres_y_apellidos"]');

                const textoID = celdaId ? celdaId.textContent.toLowerCase() : '';
                const textoNombre = celdaNombre ? celdaNombre.textContent.toLowerCase() : '';

                const filaDetalles = filaPrincipal.nextElementSibling;

                if (textoID.includes(filtro) || textoNombre.includes(filtro)) {
                    filaPrincipal.style.display = '';
                    if (filaDetalles && filaDetalles.classList.contains('fila-detalles')) {
                        if (filtro !== "") {
                            filaDetalles.style.display = 'none';
                        }
                    }
                } else {
                    filaPrincipal.style.display = 'none';
                    if (filaDetalles && filaDetalles.classList.contains('fila-detalles')) {
                        filaDetalles.style.display = 'none';
                    }
                }
            });
        });
    }


    //------------------------------------------------------
    //--------------------- CERTIFICADO --------------------
    //------------------------------------------------------
    document.addEventListener('click', function (e) {
        const btnCertificado = e.target.closest('.btn-certificado');
        if (btnCertificado) {
            e.preventDefault();
            const id = btnCertificado.dataset.id;
            // Abrimos en una pestaña nueva
            window.open(`/rrhh/empleados/certificado/${id}`, '_blank');
        }
    });

    //------------------------------------------------------
    //---------------- MODAL EDITAR CONTRATO ---------------
    //------------------------------------------------------
    document.addEventListener('click', function (e) {
        const btnContrato = e.target.closest('.btn-contrato')
        if (btnContrato) {
            const idEmpleado = btnContrato.dataset.id;
            AbrirModalEditContrato(idEmpleado);
        }
    })
    const inputSalarioEdit = document.getElementById('salario_basico_edit');
    const inputFactorEdit = document.getElementById('factor_no_salarial_edit');
    if(inputSalarioEdit){
        inputSalarioEdit.addEventListener('input', function(){
            this.value = formatoMiles(this.value);
        });
    }
    if(inputFactorEdit){
        inputFactorEdit.addEventListener('input', function(){
            this.value = formatoMiles(this.value);
        });
    }
    window.AbrirModalEditContrato = function (id) {
        fetch(`/rrhh/empleados/${id}/json`)
            .then(res => res.json())
            .then(resp => {
                if (!resp.success) return alert("Error al cargar datos");
                const emp = resp.empleado;
                document.getElementById('tituloContrato').textContent = `Edicion de contrato: ${emp.tipo_contrato} - Codigo ${emp.n_consecutivo}`
                const idContrato = parseInt(emp.tipo_contrato_id);
                const optCargo = document.getElementById('cambioCargo');
                const optSalrio = document.getElementById('cambioSalario');
                const optProrroga = document.getElementById('prorrogaContrato');
                const selectAccion = document.getElementById('accion');
                const divCargos = document.getElementById('cargos');
                const divSalarios = document.getElementById('salarios');
                const divfechasInicio = document.getElementById('fechaInicio');
                const divfechasFin = document.getElementById('fechaFin');
                const divDescripcion = document.getElementById('descripcion');
                document.getElementById('id_empleado_edit_contrato').value = emp.id;
                document.getElementById('consecutivo_edit_contrato').value = emp.n_consecutivo;
                document.getElementById('cuenta_otrosi').value = emp.cuenta_otrosi;



                if (divCargos) divCargos.style.display = 'none';
                if (divSalarios) divSalarios.style.display = 'none';
                if (divfechasInicio) divfechasInicio.style.display = 'none';
                if (divfechasFin) divfechasFin.style.display = 'none';
                if (divDescripcion) divDescripcion.style.display = 'none'

                selectAccion.value = "";

                //logica de ocultar y mostrar
                if (idContrato === 2) {
                    optProrroga.style.display = 'block';
                    optProrroga.hidden = false;
                    optProrroga.disabled = false;
                } else if(idContrato === 5){
                    optProrroga.style.display = 'block';
                    optProrroga.hidden = false;
                    optProrroga.disabled = false;
                    optCargo.style.display = 'none';
                    optSalrio.style.display = 'none';
                    optCargo.hidden = true;
                    optSalrio.hidden = true;
                    optCargo.disabled = true;
                    optSalrio.disabled = true;
                } else {
                    optProrroga.style.display = 'none';
                    optProrroga.hidden = true;
                    optProrroga.disabled = true;
                }

                if (selectAccion) {
                    selectAccion.addEventListener('change', function () {
                        if (divCargos) divCargos.style.display = 'none';
                        if (divSalarios) divSalarios.style.display = 'none';

                        if (this.value === 'cambio_cargo') {
                            divCargos.style.display = 'grid';
                            divSalarios.style.display = 'grid';
                            divDescripcion.style.display = 'block';
                            divfechasInicio.style.display = 'grid';
                        } else if (this.value === 'cambio_salario') {
                            divSalarios.style.display = 'grid';
                            divDescripcion.style.display = 'block';
                            divfechasInicio.style.display = 'grid';
                        } else if (this.value === 'prorroga') {
                            divCargos.style.display = 'none';
                            divSalarios.style.display = 'none';
                            divfechasInicio.style.display = 'grid';
                            divfechasFin.style.display = 'grid';
                            divDescripcion.style.display = 'block';
                        }
                    })
                }

                document.getElementById('modalEditContrato').classList.add('active');
            });
    }
    const formEditContrato = document.getElementById('formEditContrato');
    if (formEditContrato) {
        formEditContrato.addEventListener('submit', function (e) {
            e.preventDefault()

            const idEmpleado = document.getElementById('id_empleado_edit_contrato').value;
            const codigoContrato = document.getElementById('consecutivo_edit_contrato').value;
            const cuentaOtrosi = document.getElementById('cuenta_otrosi').value;
            const selectAccion = document.getElementById('accion');
            const accion = selectAccion.value;

            const payload = {
                accion: accion,
                cargo_id: document.getElementById('cargo_id_edit').value,
                salario: document.getElementById('salario_basico_edit').value,
                factor_salarial: document.getElementById('factor_no_salarial_edit').value,
                fecha_inicio: document.getElementById('fecha_inicio_prorroga').value,
                fecha_fin: document.getElementById('fecha_final_prorroga').value,
                descripcion: document.getElementById('descripcion_cambio').value,
                codigoContrato: codigoContrato

            };

            fetch(`/rrhh/otrosi/procesar_otrosi/${idEmpleado}`, {
                method: 'POST',
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            })
                .then(res => res.json())
                .then(resp => {
                    if(!resp.success) return alert("Error: " + resp.error)
                        alert(`Proceso de "${accion.replace('_', ' ')}" realizado con exito`);
                    location.reload();
                })
                .catch(err => alert("Error de comunicacion con el servidor"));            
        });
    }
    window.cerrarEditContrato = function () {
        const modal = document.getElementById('modalEditContrato');
        if (modal) {
            document.getElementById('modalEditContrato').classList.remove('active');
            document.getElementById('id_empleado_edit_contrato').value = "";
            document.getElementById('consecutivo_edit_contrato').value = "";
            document.getElementById('formEditContrato').reset();
        }
    };

    //------------------------------------------------------
    //----------- MODAL CONSECUTIVO DE CONTRATOS -----------
    //------------------------------------------------------
    const modalConsecutivo = document.getElementById('modalConsecutivo');
    document.addEventListener('click', function (e) {
        const btnConsecutivo = e.target.closest('.btn-consecutivo')
        if (btnConsecutivo) {
            const idContrato = btnConsecutivo.dataset.id;
            AbrirModalEditConsecutivo(idContrato);
        }
    });
    window.AbrirModalEditConsecutivo = function (id) {
        fetch(`/rrhh/contratos/${id}`)
            .then(res => res.json())
            .then(resp => {
                if (!resp.success) return alert("Error al cargar datos");
                const contrato = resp.contratos;
                document.getElementById('tituloContrato_Consecutivo').textContent = `Editar el Consecutivo para los contratos tipo: ${contrato.nombre}`;
                document.getElementById('id_contrato_consecutivo').value = id;
                const consecutvo = document.getElementById('ult_consecutivo').value = contrato.ult_consecutivo;
                modalConsecutivo.classList.add('active');
            });
    };
    window.cerrarModalConsecutivo = function () {
        modalConsecutivo.classList.remove('active');
    };
    const formConsecutivo = document.getElementById('formConsecutivo');
    if (formConsecutivo) {
        formConsecutivo.addEventListener('submit', function (e) {
            e.preventDefault()
            const id = document.getElementById('id_contrato_consecutivo').value;
            const valor = document.getElementById('ult_consecutivo').value;

            fetch(`/rrhh/contratos/consecutivo/editar/${id}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ ult_consecutivo: valor })
            })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        alert("Consecutivo actualizado con exito");
                        cerrarModalConsecutivo();
                        location.reload();
                    } else {
                        alert("error: " + data.error);
                    }
                })
                .catch(err => {
                    console.error(err);
                    alert("Error al conectar con el servidor");
                });
        });
    }
});