document.addEventListener("DOMContentLoaded", function () {

    ////////////MOSTRAR Y OCULTAR DATOS DEL FORM //////////////
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
            console.log(textoSeleccionado)

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
    ////////// SACA ANTIGUEDAD ///////////
    const fechaIngreso = document.getElementById('');
    const fechaUltimo = document.getElementById('');
    const inputAntiguedad = document.getElementById('antiguedad');

    window.calcularAntiguedad = function () {
        if (!fechaIngreso.value || !fechaUltimo.value) {
            inputAntiguedad.value = '';
            return;
        }
        const inicio = new Date(fechaIngreso.value);
        const fin = new Date(fechaUltimo.value);

        if (fin < inicio) {
            alert('La fecha del ultimo contrato no puede ser menor a la fecha de ingreso');
            inputAntiguedad.value = '';
            return;
        }
        let antiguedad = fin.getFullYear() - inicio.getFullYear();

        const mesDif = fin.getMonth() - inicio.getMonth();
        const diaDif = fin.getDate() - inicio.getDate();

        //ajusta si aun no cumple el año
        if (mesDif < 0 || (mesDif === 0 && diaDif < 0)) {
            antiguedad--
        }
        inputAntiguedad.value = antiguedad
    }
    // fechaIngreso.addEventListener('change', calcularAntiguedad);
    // fechaUltimo.addEventListener('change', calcularAntiguedad);

    ///////// calcula edad//////////
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

    //////////WIZARD PARA EL DOMAL DEL FORM ////////////
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

    ////////// submit form /////////////
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

    ////agrega filas a la tabla
    window.agregarEmpleadoTabla = function (emp) {
        const tbody = document.getElementById('tabla_lista_empleados_body');
        console.log(emp)
        const trPrincipal = document.createElement('tr');
        trPrincipal.classList.add('fila-principal');
        trPrincipal.dataset.id = emp.id;
        console.log(emp.documentos_estudio);

        trPrincipal.innerHTML = `
            <td data-column="identificacion">${emp.identificacion}</td> <!-- tipo_documento -->
            <td data-column="nombres_y_apellidos">${emp.apellidos} ${emp.nombres}</td> <!-- consecutivo -->
            <td data-column="correo">${emp.correo}</td> <!-- version -->
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
            <td colspan="6">
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
                        <button type="button" clas="btn-accion btn-docs" data-id="${emp.id}"><i class="fa-solid fa-folder-open"></i></button>
                    </span>
                    </div>
                    <div class="detalle-item"><strong>Cantidad de Contratos:</strong> <span data-column="cantidad_contratos">
                            ${emp.cantidad_contratos}                            
                        </span>
                    </div>
                </div>
            </td>
        `;
        tbody.prepend(trPrincipal);
        tbody.prepend(trDetalle);
    }

    /////// expandir filas de tabla //////////

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

    //////// botones de accion documentacion ////////

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


    ///////EDITAR EMPLEADO
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
        const fila = document.querySelector(`.fila-principal[data-id="${emp.id}"]`);
        console.log(emp);
        if (!fila) return;

        fila.querySelector('[data-column="identificacion"]').textContent = emp.identificacion;
        fila.querySelector('[data-column="nombres_y_apellidos"]').textContent = emp.apellidos + " " + emp.nombres;
        fila.querySelector('[data-column="cedula_expedida_en"]').textContent = emp.cedula_expedida_en;
        fila.querySelector('[data-column="sexo"]').textContent = emp.sexo;
        fila.querySelector('[data-column="fecha_nacimiento"]').textContent = emp.fecha_nacimiento;
        fila.querySelector('[data-column="lugar_nacimiento"]').textContent = emp.lugar_nacimiento;
        fila.querySelector('[data-column="edad"]').textContent = emp.edad;
        fila.querySelector('[data-column="estado_civil_id"]').textContent = emp.estado_civil_id;
        fila.querySelector('[data-column="grupo_sanguineo_id"]').textContent = emp.grupo_sanguineo_id;
        fila.querySelector('[data-column="numero_hijos"]').textContent = emp.numero_hijos;
        fila.querySelector('[data-column="direccion"]').textContent = emp.direccion;
        fila.querySelector('[data-column="barrio"]').textContent = emp.barrio;
        fila.querySelector('[data-column="localidad"]').textContent = emp.localidad;
        fila.querySelector('[data-column="estrato"]').textContent = emp.estrato;
        fila.querySelector('[data-column="telefono_fijo"]').textContent = emp.telefono_fijo;
        fila.querySelector('[data-column="celular"]').textContent = emp.celular;
        fila.querySelector('[data-column="correo"]').textContent = emp.correo;
        fila.querySelector('[data-column="contacto_emergencia"]').textContent = emp.contacto_emergencia;
        fila.querySelector('[data-column="telefono_emergencia"]').textContent = emp.telefono_emergencia;
        fila.querySelector('[data-column="parentesco"]').textContent = emp.parentesco;
        fila.querySelector('[data-column="eps_id"]').textContent = emp.eps_id;
        fila.querySelector('[data-column="afp_id"]').textContent = emp.afp_id;
        fila.querySelector('[data-column="cesantias_id"]').textContent = emp.cesantias_id;
        fila.querySelector('[data-column="ccf_id"]').textContent = emp.ccf_id;
        fila.querySelector('[data-column="arl_id"]').textContent = emp.arl_id;
        fila.querySelector('[data-column="tipo_contrato_id"]').textContent = emp.tipo_contrato_id;
        fila.querySelector('[data-column="cargo_id"]').textContent = emp.cargo_id;
        fila.querySelector('[data-column="jornada"]').textContent = emp.jornada;
        fila.querySelector('[data-column="sede"]').textContent = emp.sede;
        fila.querySelector('[data-column="fecha_ingreso_antigua"]').textContent = emp.fecha_ingreso;
        fila.querySelector('[data-column="antiguedad"]').textContent = emp.antiguedad;
        fila.querySelector('[data-column="salario_basico"]').textContent = emp.salario_basico;
        fila.querySelector('[data-column="factor_no_salarial"]').textContent = emp.factor_no_salarial;
        fila.querySelector('[data-column="numero_cuenta"]').textContent = emp.numero_cuenta;
        fila.querySelector('[data-column="banco"]').textContent = emp.banco;
        fila.querySelector('[data-column="grupo_nomina_id"]').textContent = emp.grupo_nomina_id;
        fila.querySelector('[data-column="nivel_escolaridad_id"]').textContent = emp.nivel_escolaridad_id;
        fila.querySelector('[data-column="programa_academico"]').textContent = emp.programa_academico;
        fila.querySelector('[data-column="estudia_actualmente"]').textContent = emp.estudia_actualmente;
        fila.querySelector('[data-column="nombre_programa_actual"]').textContent = emp.nombre_programa_actual;
    };

    ///descativar empleado
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
            body: JSON.stringify({ fecha_retiro: fechaRetiro })
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


    ////activar empleado
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
        if (!fechaIngreso) {
            alert("Por favor ingrese una fecha de ingreso");
            return;
        }
        fetch(`/rrhh/empleados/activar/${empleadoActivarId}`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            }, 
            body: JSON.stringify({ fecha_ingreso: fechaIngreso })
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


        //select2
        $(document).ready(function () {
            $('.select2_barrio').select2({
                placeholder: 'Buscar...',
                allowClear: true,
                width: '100%',
                dropdownParent: $('#modalEmpleado')
            });
        });

        //formato dinero
        window.formatoMiles = function (valor) {
            valor = valor.replace(/[\D]/g, "");
            if (valor === '') return;

            return parseInt(valor, 10).toLocaleString('es-CO');
        }
        const inputSalario = document.getElementById('salario_basico');
        const factor_no_salarial = document.getElementById("factor_no_salarial");
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

        ///modal fecha retiro
        window.cerrarModalRetiro = function () {
            const modal = document.getElementById('modalRetiro');
            modal.classList.remove('active');
        }
        //modal contratos
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
                        console.log(resp.contratos);
                        const tbody = document.getElementById('tabla_contratos_empleado_body');
                        tbody.innerHTML = '';
                        resp.contratos.forEach(contrato => {
                            const tr = document.createElement('tr');
                            tr.innerHTML = `
                                <td style="color: black;" data-column="tipo_contrato">${contrato.tipo_contrato}</td>
                                <td style="color: black;" data-column="fecha_inicio">${contrato.fecha_ingreso}</td>
                                <td style="color: black;" data-column="fecha_fin">${contrato.fecha_finalizacion}</td>
                            `;
                            tbody.appendChild(tr);
                        });
                    })
                    .catch(err => {
                        console.error(err);
                        alert('Error en el servidor');
                    });
            }
        });
        window.cerrarModalContratos = function () {
            const modal = document.getElementById('modalContratos');
            modal.classList.remove('active');
        }
    });