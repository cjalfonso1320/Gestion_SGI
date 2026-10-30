// getBaseUrl debe estar en window para que sea accesible desde modales inline en home.html
window.getBaseUrl = function() { return (typeof BASE_URL !== 'undefined' && BASE_URL) ? BASE_URL : (window.BASE_URL || ''); };

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
    //--------- FORMATO MONEDA PARA MOSTRAR ($2.000.000) --
    //------------------------------------------------------
    window.formatearMoneda = function (valor, conSimbolo) {
        if (valor === null || valor === undefined || valor === '') return '';
        const num = Number(valor);
        if (isNaN(num)) return '';
        const texto = num.toLocaleString('es-CO', { maximumFractionDigits: 2 });
        // conSimbolo = false → solo miles ("2.000.000") para los inputs editables
        return conSimbolo === false ? texto : '$' + texto;
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
                Swal.fire('Error', 'La fecha de nacimiento no puede ser mayor a hoy', 'error');
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
    const progressSteps = document.querySelectorAll('.wizard-progress-step');
    const btnGuardar = document.getElementById('btnGuardar');
    const btnSiguiente = document.getElementById('btnSiguiente');
    const btnAnterior = document.getElementById('btnAnterior');
    const stepCounter = document.getElementById('stepCounter');
    const modalTitulo = document.getElementById('modalEmpleadoTitulo');

    function showStep(index, direction) {
        // Remover animaciones previas
        steps.forEach(s => s.classList.remove('animating-next', 'animating-prev'));

        // Mostrar/ocultar pasos
        steps.forEach((step, i) => {
            step.classList.toggle('active', i === index);
            if (i === index) {
                // Añadir animación según dirección
                if (direction === 'prev') {
                    step.classList.add('animating-prev');
                } else {
                    step.classList.add('animating-next');
                }
            }
        });

        // Actualizar progress indicator
        progressSteps.forEach((step, i) => {
            const circle = step.querySelector('.wizard-progress-circle');
            step.classList.remove('active', 'completed');
            if (i < index) {
                step.classList.add('completed');
                if (circle) circle.innerHTML = '<i class="fa-solid fa-check"></i>';
            } else if (i === index) {
                step.classList.add('active');
                if (circle) circle.textContent = i + 1;
            } else {
                if (circle) circle.textContent = i + 1;
            }
        });

        // Actualizar líneas de progreso
        document.querySelectorAll('.wizard-progress-line').forEach((line, i) => {
            line.classList.toggle('completed', i < index);
        });

        // Botones
        if (btnGuardar && btnSiguiente) {
            const isLast = index === steps.length - 1;
            btnGuardar.style.display = isLast ? 'inline-flex' : 'none';
            btnSiguiente.style.display = isLast ? 'none' : 'inline-flex';
        }

        // Botón anterior
        if (btnAnterior) {
            btnAnterior.style.visibility = index === 0 ? 'hidden' : 'visible';
        }

        // Contador
        if (stepCounter) {
            stepCounter.textContent = `Paso ${index + 1} de ${steps.length}`;
        }
    }

    //--- VALIDACIÓN DE CAMPOS REQUERIDOS POR PASO ---
    // Mapa de campos requeridos por paso del wizard (índice del paso)
    const camposRequeridosPorPaso = {
        0: [ // Paso 1: Datos Personales
            { id: 'identificacion', nombre: 'N° Identificación' },
            { id: 'tipo_identificacion', nombre: 'Tipo de Identificación' },
            { id: 'nombres', nombre: 'Nombres' },
            { id: 'apellidos', nombre: 'Apellidos' },
            { id: 'cedula_expedida_en', nombre: 'Cédula Expedida en' },
            { id: 'sexo', nombre: 'Sexo' },
            { id: 'fecha_nacimiento', nombre: 'Fecha de Nacimiento' },
            { id: 'lugar_nacimiento', nombre: 'Lugar de Nacimiento' },
            { id: 'estado_civil_id', nombre: 'Estado Civil' },
            { id: 'grupo_sanguineo_id', nombre: 'Grupo Sanguíneo' },
            { id: 'numero_hijos', nombre: 'N° de Hijos' },
        ],
        1: [ // Paso 2: Contacto
            { id: 'direccion', nombre: 'Dirección' },
            { id: 'barrio', nombre: 'Ciudad/Municipio' },
            { id: 'estrato', nombre: 'Estrato' },
            { id: 'celular', nombre: 'Celular' },
            { id: 'correo', nombre: 'Correo Electrónico' },
            { id: 'contacto_emergencia', nombre: 'Contacto de Emergencia' },
            { id: 'telefono_emergencia', nombre: 'Teléfono de Emergencia' },
            { id: 'parentesco', nombre: 'Parentesco' },
        ],
        2: [ // Paso 3: Seguridad Social
            { id: 'eps_id', nombre: 'EPS' },
            { id: 'afp_id', nombre: 'AFP' },
            { id: 'cesantias_id', nombre: 'Cesantías' },
            { id: 'ccf_id', nombre: 'CCF' },
            { id: 'arl_id', nombre: 'ARL' },
        ],
        3: [ // Paso 4: Información Laboral
            { id: 'tipo_contrato_id', nombre: 'Tipo de Contrato' },
            { id: 'cargo_id', nombre: 'Cargo' },
            { id: 'salario_basico', nombre: 'Salario Básico' },
            { id: 'numero_cuenta', nombre: 'N° Cuenta' },
            { id: 'banco', nombre: 'Banco' },
            { id: 'grupo_nomina_id', nombre: 'Grupo de Nómina' },
        ],
        4: [ // Paso 5: Información Educativa
            { id: 'nivel_escolaridad_id', nombre: 'Nivel Escolaridad' },
            { id: 'programa_academico', nombre: 'Programa Académico' },
            { id: 'estudia_actualmente', nombre: 'Estudia Actualmente' },
        ],
    };

    /**
     * Valida los campos requeridos de un paso específico.
     * Retorna { valido: bool, faltantes: string[] }.
     */
    function validarPaso(pasoIndex) {
        const campos = camposRequeridosPorPaso[pasoIndex];
        if (!campos) return { valido: true, faltantes: [] };

        const faltantes = [];
        campos.forEach(campo => {
            const el = document.getElementById(campo.id);
            if (!el) return;
            const valor = (el.value || '').trim();
            // Select con value="" (placeholder "Seleccione uno...") se considera vacío
            if (!valor) {
                faltantes.push(campo.nombre);
            }
        });
        return { valido: faltantes.length === 0, faltantes };
    }

    /**
     * Muestra alerta SweetAlert2 con los campos faltantes y resalta los campos.
     */
    function mostrarAlertaCamposFaltantes(faltantes) {
        const listaHtml = faltantes.map(f => `• ${f}`).join('<br>');
        Swal.fire({
            title: 'Campos obligatorios incompletos',
            html: `Por favor completa los siguientes campos:<br><br>${listaHtml}`,
            icon: 'warning',
            confirmButtonColor: '#1a73e8',
            confirmButtonText: 'Entendido',
            customClass: { popup: 'swal-campos-faltantes' }
        });
    }

    /**
     * Resalta visualmente los campos faltantes de un paso.
     */
    function resaltarCamposFaltantes(pasoIndex) {
        const campos = camposRequeridosPorPaso[pasoIndex];
        if (!campos) return;
        // Quitar resaltado previo
        document.querySelectorAll('.form-control, .select2-container, select').forEach(el => {
            el.style.borderColor = '';
        });
        campos.forEach(campo => {
            const el = document.getElementById(campo.id);
            if (!el) return;
            const valor = (el.value || '').trim();
            if (!valor) {
                // Resaltar en rojo el input o el select
                el.style.borderColor = '#dc3545';
            }
        });
        // También resaltar select2 (el real está oculto, el visible es .select2-container)
        campos.forEach(campo => {
            const el = document.getElementById(campo.id);
            if (!el) return;
            const valor = (el.value || '').trim();
            if (!valor && el.tagName === 'SELECT') {
                const select2 = el.nextElementSibling;
                if (select2 && select2.classList.contains('select2-container')) {
                    select2.style.borderColor = '#dc3545';
                    select2.style.border = '2px solid #dc3545';
                }
            }
        });
    }

    /**
     * Quitar resaltado rojo de todos los campos del paso.
     */
    function limpiarResaltado(pasoIndex) {
        const campos = camposRequeridosPorPaso[pasoIndex];
        if (!campos) return;
        campos.forEach(campo => {
            const el = document.getElementById(campo.id);
            if (!el) return;
            el.style.borderColor = '';
            if (el.tagName === 'SELECT') {
                const select2 = el.nextElementSibling;
                if (select2 && select2.classList.contains('select2-container')) {
                    select2.style.borderColor = '';
                    select2.style.border = '';
                }
            }
        });
    }

    window.nextStep = function () {
        // Validar campos del paso actual antes de avanzar
        const resultado = validarPaso(currenStep);
        if (!resultado.valido) {
            mostrarAlertaCamposFaltantes(resultado.faltantes);
            resaltarCamposFaltantes(currenStep);
            return; // No avanzar
        }
        // Limpiar resaltado y avanzar
        limpiarResaltado(currenStep);
        if (currenStep < steps.length - 1) {
            currenStep++;
            showStep(currenStep, 'next')
        }
    };
    window.prevStep = function () {
        if (currenStep > 0) {
            currenStep--;
            showStep(currenStep, 'prev')
        }
    };
    // Helper: actualizar preview de cédula en modal de edición
    window.actualizarCedulaPreview = function (cedulaPath) {
        const preview = document.getElementById('cedulaPreview');
        if (!preview) return;

        if (cedulaPath) {
            const ext = cedulaPath.split('.').pop().toLowerCase();
            const fileName = cedulaPath.split('/').pop() || 'Cédula';
            preview.classList.add('has-file');

            if (['jpg','jpeg','png','tiff','webp'].includes(ext)) {
                // Es imagen: mostrar thumbnail
                preview.innerHTML = '<img src="" alt="Cédula"><span class="cedula-preview-text">' + ext.toUpperCase() + '</span>';
                const imgEl = preview.querySelector('img');
                if (imgEl) {
                    imgEl.src = getBaseUrl() + '/' + cedulaPath.replace(/\\/g, '/');
                    imgEl.onerror = function() { this.style.display = 'none'; };
                }
            } else {
                // Es PDF u otro: mostrar icono y nombre de archivo
                preview.innerHTML = '<i class="' + (ext === 'pdf' ? 'fa-regular fa-file-pdf' : 'fa-regular fa-id-card') + '"></i><span class="cedula-preview-text">' + fileName + '</span>';
            }
            // Hacer clic abre la vista previa completa
            preview.onclick = function() {
                window.abrirArchivo && abrirArchivo(cedulaPath.replace(/\\/g, '/'), 'Cédula');
            };
            preview.title = 'Ver Cédula';
            preview.style.cursor = 'pointer';
        } else {
            resetearCedulaPreview();
        }
    };

    window.resetearCedulaPreview = function () {
        const preview = document.getElementById('cedulaPreview');
        if (!preview) return;
        preview.classList.remove('has-file');
        preview.innerHTML = '<i class="fa-regular fa-id-card"></i><span class="cedula-preview-text">Sin archivo</span>';
        preview.onclick = null;
        preview.title = '';
        preview.style.cursor = 'default';
    };

    window.abrirModalEmpleado = function () {
        currenStep = 0;
        // Reset modal title a "Nuevo Empleado" solo si NO es edición
        // (al editar, abrirModalEditarEmpleado ya definió el título y dataset.editId)
        const formEmp = document.getElementById('form_Empleado');
        if (modalTitulo && !(formEmp && formEmp.dataset.editId)) {
            modalTitulo.innerHTML = '<i class="fa-solid fa-user-plus"></i> Nuevo Empleado';
        }
        showStep(currenStep);
        document.getElementById('modalEmpleado')?.classList.add('active');
    };
    window.cerrarModalEmpleado = function () {
        document.getElementById('modalEmpleado')?.classList.remove('active');
        // Limpiar foto preview al cerrar
        const fp = document.getElementById('fotoPreview');
        if (fp) fp.src = getBaseUrl() + '/static/imgs/user.png';
        // Limpiar cédula preview al cerrar
        resetearCedulaPreview();
    };
    showStep(currenStep);

    //------------------------------------------------------
    //------------ SUBMIT DE FORM NUEVO EMPLEADO -----------
    //------------------------------------------------------
    const formEmpleado = document.getElementById('form_Empleado');
    if (formEmpleado) {
        formEmpleado.addEventListener('submit', function (e) {
            e.preventDefault();

            // Validar TODOS los pasos antes de enviar
            let todosFaltantes = [];
            for (let i = 0; i <= 4; i++) {
                const resultado = validarPaso(i);
                if (!resultado.valido) {
                    todosFaltantes = todosFaltantes.concat(resultado.faltantes);
                }
            }
            if (todosFaltantes.length > 0) {
                // Encontrar el primer paso con errores y navegar a él
                for (let i = 0; i <= 4; i++) {
                    const resultado = validarPaso(i);
                    if (!resultado.valido) {
                        currenStep = i;
                        showStep(currenStep, 'prev');
                        resaltarCamposFaltantes(i);
                        break;
                    }
                }
                mostrarAlertaCamposFaltantes(todosFaltantes);
                return;
            }
            // Limpiar resaltado
            for (let i = 0; i <= 4; i++) {
                limpiarResaltado(i);
            }

            const form = this
            // La antigüedad se muestra en texto ("3 años 5 meses") pero en BD
            // solo se guardan los años (columna numérica). Extraer los años.
            const campoAntiguedad = document.getElementById('antiguedad');
            if (campoAntiguedad) {
                const val = (campoAntiguedad.value || '').trim();
                const match = val.match(/(\d+)\s*años?/);
                if (match) {
                    campoAntiguedad.value = match[1];
                } else if (/^\d+$/.test(val)) {
                    campoAntiguedad.value = val;
                } else {
                    campoAntiguedad.value = '0';
                }
            }
            const data = new FormData(form);

            //detecta si es edicion
            const editId = form.dataset.editId;
            let url = `${getBaseUrl()}/rrhh/empleados/crear`;
            if (editId) {
                url = `${getBaseUrl()}/rrhh/empleados/editar/${editId}`;
            }

            fetch(url, {
                method: 'POST',
                body: data
            })
                .then(res => {
                    if (!res.ok) {
                        return res.text().then(text => {
                            throw new Error(text || `HTTP ${res.status}`);
                        });
                    }
                    return res.json();
                })
                .then(resp => {
                    if (!resp.success) {
                        Swal.fire('Error', resp.error, 'error');
                        return;
                    }
                    resp.empleado.documentos_estudio = resp.documentos_estudio
                    if (editId) {
                        Swal.fire('Éxito', 'Empleado Actualizado', 'success');
                        window.actualizarFilaEmpleado(resp.empleado);
                    } else {
                        Swal.fire('Éxito', 'Empleado Creado Correctamente', 'success');
                        window.agregarEmpleadoTabla(resp.empleado);
                    }
                    window.cerrarModalEmpleado();
                    form.reset();
                    delete form.dataset.editId;
                    document.getElementById("btnGuardar").textContent = "Guardar";
                })
                .catch(err => {
                    console.error(err);
                    Swal.fire('Error', 'Error al actualizar empleado: ' + err.message, 'error');
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
            <td data-column="nombres_y_apellidos">
                <div class="emp-name-cell">
                    <img src="${emp.foto_path ? (getBaseUrl() + '/' + emp.foto_path.replace(/\\/g, '/')) : getBaseUrl() + '/static/imgs/user.png'}"
                         class="emp-photo-thumb"
                         onerror="this.onerror=null;this.src=getBaseUrl()+'/static/imgs/user.png'">
                    <span>${emp.apellidos} ${emp.nombres}</span>
                </div>
            </td> <!-- consecutivo -->
            <td data-column="cargo">${emp.cargos}</td> <!-- nombre_documento -->
            <td data-column="tipo_contrato">${emp.tipo_contrato}</td> <!-- fecha_ultima_revision -->
            <td class="acciones">
                <button type="button" class="btn-accion btn-foto btn-preview"
                    data-url="${emp.cedula_path ? emp.cedula_path.replace(/\\/g, '/') : ''}" data-tipo="cedula" title="Ver Cédula"><i
                        class="fa-regular fa-id-card"></i>${emp.cedula_path ? '<span class="file-dot"></span>' : ''}</button>
                <button type="button" class="btn-accion btn-foto btn-preview"
                    data-url="${emp.foto_path ? emp.foto_path.replace(/\\/g, '/') : ''}" data-tipo="foto" title="Ver Foto"><i
                        class="fa-solid fa-image-portrait"></i>${emp.foto_path ? '<span class="file-dot"></span>' : ''}</button>
                <button type="button" class="btn-accion btn-contrato" data-id="${emp.id}" title="Modificar Contrato"><i class="fa-solid fa-user-tie"></i>${emp.cantidad_contratos > 0 ? '<span class="btn-badge">' + emp.cantidad_contratos + '</span>' : ''}</button>
                <button type="button" class="btn-accion btn-editar" data-id="${emp.id}" title="Editar Empleado"><i class="fa-solid fa-user-pen"></i></button>
                <button type="button" class="btn-accion btn-restablecer" data-id="${emp.id}" title="Restablecer Contraseña"><i class="fa-solid fa-key"></i></button>
                <button type="button" class="btn-accion btn-eliminar" data-id="${emp.id}" title="Retirar Empleado"><i class="fa-solid fa-person-circle-minus"></i></button>
                <button type="button" class="btn-accion btn-eliminar-def" data-id="${emp.id}" title="Eliminar Definitivamente (requiere contraseña)"><i class="fa-solid fa-trash-can"></i></button>
            </td>
        `;

        const trDetalle = document.createElement('tr');
        trDetalle.classList.add('fila-detalles');
        trDetalle.style.display = 'none';
        // Usar la misma estructura de pestañas que el template Jinja2
        trDetalle.innerHTML = `
            <td colspan="5">
                <div class="detalle-tabs">
                    <div class="detalle-tab-nav" data-empleado-id="${emp.id}">
                        <button class="detalle-tab-btn active" data-tab="personales" onclick="switchDetalleTab(this, 'personales')">
                            <i class="fa-solid fa-user"></i> Personales
                        </button>
                        <button class="detalle-tab-btn" data-tab="contacto" onclick="switchDetalleTab(this, 'contacto')">
                            <i class="fa-solid fa-phone"></i> Contacto
                        </button>
                        <button class="detalle-tab-btn" data-tab="seguridad" onclick="switchDetalleTab(this, 'seguridad')">
                            <i class="fa-solid fa-shield-heart"></i> Seg. Social
                        </button>
                        <button class="detalle-tab-btn" data-tab="laboral" onclick="switchDetalleTab(this, 'laboral')">
                            <i class="fa-solid fa-briefcase"></i> Laboral
                        </button>
                        <button class="detalle-tab-btn" data-tab="educacion" onclick="switchDetalleTab(this, 'educacion')">
                            <i class="fa-solid fa-graduation-cap"></i> Educación
                        </button>
                        <button class="detalle-tab-btn" data-tab="documentos" onclick="switchDetalleTab(this, 'documentos')">
                            <i class="fa-solid fa-folder"></i> Documentos
                        </button>
                    </div>

                    <div class="detalle-tab-panel active" data-tab="personales">
                        <div class="detalle-personales-layout">
                            <div class="detalle-foto-col">
                                <img src="${emp.foto_path ? (getBaseUrl() + '/' + emp.foto_path.replace(/\\/g, '/')) : getBaseUrl() + '/static/imgs/user.png'}"
                                     class="emp-photo-detail"
                                     onerror="this.onerror=null;this.src=getBaseUrl()+'/static/imgs/user.png'">
                            </div>
                            <div class="detalles-contenido">
                            <div class="detalle-item"><strong>Tipo Identificación:</strong> <span data-column="tipo_doc_nombre">${emp.tipo_doc_nombre || ''}</span></div>
                            <div class="detalle-item"><strong>Cédula Expedida en:</strong> <span data-column="cedula_expedida_en">${emp.cedula_expedida_en || ''}</span></div>
                            <div class="detalle-item"><strong>Sexo:</strong> <span data-column="sexo">${emp.sexo || ''}</span></div>
                            <div class="detalle-item"><strong>Fecha Nacimiento:</strong> <span data-column="fecha_nacimiento">${emp.fecha_nacimiento || ''}</span></div>
                            <div class="detalle-item"><strong>Lugar Nacimiento:</strong> <span data-column="lugar_nacimiento">${emp.lugar_nacimiento || ''}</span></div>
                            <div class="detalle-item"><strong>Edad:</strong> <span data-column="edad">${emp.edad || ''} Años</span></div>
                            <div class="detalle-item"><strong>Estado Civil:</strong> <span data-column="estado_civil_id">${emp.estado_civil || ''}</span></div>
                            <div class="detalle-item"><strong>Grupo Sanguíneo:</strong> <span data-column="grupo_sanguineo_id">${emp.grupo_sanguineo || ''}</span></div>
                            <div class="detalle-item"><strong>N° Hijos:</strong> <span data-column="numero_hijos">${emp.numero_hijos || ''}</span></div>
                        </div>
                        </div>
                    </div>

                    <div class="detalle-tab-panel" data-tab="contacto">
                        <div class="detalles-contenido">
                            <div class="detalle-item"><strong>Dirección:</strong> <span data-column="direccion">${emp.direccion || ''}</span></div>
                            <div class="detalle-item"><strong>Ciudad:</strong> <span data-column="barrio">${emp.barrio || ''}</span></div>
                            <div class="detalle-item"><strong>Barrio:</strong> <span data-column="barrio2">${emp.barrio2 || ''}</span></div>
                            <div class="detalle-item"><strong>Localidad:</strong> <span data-column="localidad">${emp.localidad || ''}</span></div>
                            <div class="detalle-item"><strong>Estrato:</strong> <span data-column="estrato">${emp.estrato || ''}</span></div>
                            <div class="detalle-item"><strong>Teléfono Fijo:</strong> <span data-column="telefono_fijo">${emp.telefono_fijo || ''}</span></div>
                            <div class="detalle-item"><strong>Celular:</strong> <span data-column="celular">${emp.celular || ''}</span></div>
                            <div class="detalle-item"><strong>Correo:</strong> <span data-column="correo">${emp.correo || ''}</span></div>
                            <div class="detalle-item"><strong>Contacto Emergencia:</strong> <span data-column="contacto_emergencia">${emp.contacto_emergencia || ''}</span></div>
                            <div class="detalle-item"><strong>Tel. Emergencia:</strong> <span data-column="telefono_emergencia">${emp.telefono_emergencia || ''}</span></div>
                            <div class="detalle-item"><strong>Parentesco:</strong> <span data-column="parentesco">${emp.parentesco || ''}</span></div>
                        </div>
                    </div>

                    <div class="detalle-tab-panel" data-tab="seguridad">
                        <div class="detalles-contenido">
                            <div class="detalle-item"><strong>EPS:</strong> <span data-column="eps_id">${emp.eps || ''}</span></div>
                            <div class="detalle-item"><strong>AFP:</strong> <span data-column="afp_id">${emp.afp || ''}</span></div>
                            <div class="detalle-item"><strong>Cesantías:</strong> <span data-column="cesantias_id">${emp.cesantias || ''}</span></div>
                            <div class="detalle-item"><strong>CCF:</strong> <span data-column="ccf_id">${emp.ccf || ''}</span></div>
                            <div class="detalle-item"><strong>ARL:</strong> <span data-column="arl_id">${emp.arl || ''}</span></div>
                        </div>
                    </div>

                    <div class="detalle-tab-panel" data-tab="laboral">
                        <div class="detalles-contenido">
                            <div class="detalle-item"><strong>Tipo Contrato:</strong> <span data-column="tipo_contrato">${emp.tipo_contrato || ''}</span></div>
                            <div class="detalle-item"><strong>Jornada:</strong> <span data-column="jornada">${emp.jornada || ''}</span></div>
                            <div class="detalle-item"><strong>Sede:</strong> <span data-column="sede">${emp.sedes || ''}</span></div>
                            <div class="detalle-item"><strong>Fecha Ingreso:</strong> <span data-column="fecha_ingreso">${emp.fecha_ingreso || ''}</span></div>
                            <div class="detalle-item"><strong>Antigüedad:</strong> <span data-column="antiguedad">${emp.antiguedad_texto || (emp.antiguedad ? emp.antiguedad + ' Años' : '')}</span></div>
                            <div class="detalle-item"><strong>Salario Básico:</strong> <span data-column="salario_basico">${window.formatearMoneda(emp.salario_basico)}</span></div>
                            <div class="detalle-item"><strong>Factor No Salarial:</strong> <span data-column="factor_no_salarial">${window.formatearMoneda(emp.factor_no_salarial)}</span></div>
                            <div class="detalle-item"><strong>N° Cuenta:</strong> <span data-column="numero_cuenta">${emp.numero_cuenta || ''}</span></div>
                            <div class="detalle-item"><strong>Banco:</strong> <span data-column="banco">${emp.bancos || ''}</span></div>
                            <div class="detalle-item"><strong>Grupo Nómina:</strong> <span data-column="grupo_nomina_id">${emp.grupo_nomina || ''}</span></div>
                            <div class="detalle-item"><strong>Rol SGI:</strong> <span data-column="sgi_rol">${emp.sgi_rol || 'Sin acceso'}</span></div>
                        </div>
                    </div>

                    <div class="detalle-tab-panel" data-tab="educacion">
                        <div class="detalles-contenido">
                            <div class="detalle-item"><strong>Nivel Escolaridad:</strong> <span data-column="nivel_escolaridad_id">${emp.nivel_escolaridad || ''}</span></div>
                            <div class="detalle-item"><strong>Programa Académico:</strong> <span data-column="programa_academico">${emp.programa_academico || ''}</span></div>
                            <div class="detalle-item"><strong>Estudia Actualmente:</strong> <span data-column="estudia_actualmente">${emp.estudia_actualmente || ''}</span></div>
                            <div class="detalle-item"><strong>Programa Actual:</strong> <span data-column="nombre_programa_actual">${emp.nombre_programa_actual || ''}</span></div>
                        </div>
                    </div>

                    <div class="detalle-tab-panel" data-tab="documentos">
                        <div class="detalles-contenido">
                            <div class="detalle-item"><strong>Documentos de Estudio:</strong>
                                <button type="button" class="btn-accion btn-docs" data-id="${emp.id}" title="Ver Documentos de Estudio">
                                    <i class="fa-solid fa-folder-open"></i> Ver documentos
                                </button>
                            </div>
                            <div class="detalle-item"><strong>Contratos:</strong>
                                <span>${emp.cantidad_contratos || 0}</span>
                                <button type="button" class="btn-accion btn-contratos" data-id="${emp.id}" title="Ver Contratos">
                                    <i class="fa-solid fa-eye"></i> Ver contratos
                                </button>
                            </div>
                            <div class="detalle-item"><strong>Certificado Laboral:</strong>
                                <button type="button" class="btn-accion btn-certificado" data-id="${emp.id}" title="Generar Certificado">
                                    <i class="fa-solid fa-file-pdf"></i> Generar Certificado
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </td>
        `;
        tbody.prepend(trDetalle);
        tbody.prepend(trPrincipal);

        // Re-aplicar filtros activos (búsqueda / tipo de contrato) a la nueva fila
        if (window.aplicarFiltrosEmpleados) window.aplicarFiltrosEmpleados();
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
            if (!btnDocs.dataset.id) return;
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
        const tipo = btn.dataset.tipo;
        const nombreDoc = tipo === 'cedula' ? 'Cédula' : tipo === 'foto' ? 'Foto' : 'Documento';
        abrirArchivo(btn.dataset.url, nombreDoc);
    });

    window.abrirListaDocumentos = function (docs) {
        window.docActuales = docs;
        const modal = document.getElementById("modalPreview");
        const lista = document.getElementById("previewListaDocs");
        const img = document.getElementById("previewImg");
        const pdf = document.getElementById("previewPdf");
        const loader = document.getElementById("previewLoader");
        const error = document.getElementById("previewError");
        const title = document.getElementById("modalPreviewTitle");

        // Ocultar loader, error, img, pdf
        if (loader) loader.style.display = 'none';
        if (error) error.style.display = 'none';
        img.style.display = 'none';
        pdf.style.display = 'none';
        lista.style.display = 'block';

        if (title) title.innerHTML = '<i class="fa-solid fa-folder-open"></i> Documentos de Estudio';

        // Construir lista de documentos
        const container = document.getElementById("listaDocsContainer");
        if (!container) return;
        container.innerHTML = '';

        if (docs.length === 0) {
            container.innerHTML = `
                <div class="preview-empty">
                    <i class="fa-regular fa-folder-open"></i>
                    <p>No hay documentos cargados</p>
                </div>
            `;
        } else {
            docs.forEach((ruta, i) => {
                const ext = ruta.split('.').pop().toLowerCase();
                let iconClass = 'icon-default';
                let iconHtml = '<i class="fa-regular fa-file-lines"></i>';
                if (['jpg','jpeg','png','tiff','webp'].includes(ext)) {
                    iconClass = 'icon-image';
                    iconHtml = '<i class="fa-regular fa-file-image"></i>';
                } else if (ext === 'pdf') {
                    iconClass = 'icon-pdf';
                    iconHtml = '<i class="fa-regular fa-file-pdf"></i>';
                }
                const card = document.createElement('button');
                card.className = 'doc-card-item';
                card.innerHTML = `
                    <div class="doc-card-icon ${iconClass}">${iconHtml}</div>
                    <div class="doc-card-info">
                        <span class="doc-card-name">Documento ${i + 1}</span>
                        <span class="doc-card-meta">${ext.toUpperCase()} — ${ruta.split('/').pop()}</span>
                    </div>
                    <span class="doc-card-arrow"><i class="fa-solid fa-chevron-right"></i></span>
                `;
                card.addEventListener('click', function() {
                    abrirArchivo(ruta, 'Documento ' + (i + 1));
                });
                container.appendChild(card);
            });
        }

        document.getElementById("btnVolverLista").style.display = 'none';
        modal.classList.add("active")
    }
    window.abrirArchivo = function (url, nombreDoc) {
        const modal = document.getElementById("modalPreview");
        const lista = document.getElementById("previewListaDocs");
        const img = document.getElementById("previewImg");
        const pdf = document.getElementById("previewPdf");
        const loader = document.getElementById("previewLoader");
        const errorEl = document.getElementById("previewError");
        const title = document.getElementById("modalPreviewTitle");

        // Ocultar todo
        img.style.display = 'none';
        pdf.style.display = 'none';
        lista.style.display = 'none';
        if (loader) loader.style.display = 'none';
        if (errorEl) errorEl.style.display = 'none';

        if (!url) {
            Swal.fire('Información', 'No hay archivo disponible para visualizar', 'info');
            return;
        }

        // Actualizar título
        nombreDoc = nombreDoc || 'Documento';
        if (title) {
            const ext = url.split('.').pop().toLowerCase();
            let icon = 'fa-regular fa-file-image';
            if (ext === 'pdf') icon = 'fa-regular fa-file-pdf';
            title.innerHTML = `<i class="${icon}"></i> ${nombreDoc}`;
        }

        document.getElementById("btnVolverLista").style.display = "inline-block";
        modal.classList.add("active");

        const base = getBaseUrl();
        const fullUrl = base + '/' + url;

        if (url.match(/\.(jpg|jpeg|png|tiff|webp)$/i)) {
            // Show loader
            if (loader) loader.style.display = 'flex';

            img.onload = function () {
                if (loader) loader.style.display = 'none';
                if (errorEl) errorEl.style.display = 'none';
                img.style.display = 'block';
            };
            img.onerror = function () {
                if (loader) loader.style.display = 'none';
                img.style.display = 'none';
                if (errorEl) {
                    errorEl.style.display = 'flex';
                    errorEl.querySelector('span').textContent = 'Error al cargar la imagen';
                }
            };
            img.src = fullUrl;

        } else if (url.match(/\.pdf$/i)) {
            // Show loader
            if (loader) loader.style.display = 'flex';

            // Timeout fallback for PDF (iframe onerror no es confiable)
            const pdfTimeout = setTimeout(function () {
                if (loader) loader.style.display = 'none';
                if (errorEl) {
                    errorEl.style.display = 'flex';
                    errorEl.querySelector('span').textContent = 'Error al cargar el PDF — tiempo de espera agotado';
                }
            }, 15000);

            pdf.onload = function () {
                clearTimeout(pdfTimeout);
                if (loader) loader.style.display = 'none';
                if (errorEl) errorEl.style.display = 'none';
                pdf.style.display = 'block';
            };
            pdf.src = fullUrl;
        }
    }
    window.cerrarPreview = function () {
        const modal = document.getElementById('modalPreview');
        const img = document.getElementById('previewImg');
        const pdf = document.getElementById('previewPdf');
        const loader = document.getElementById('previewLoader');
        const errorEl = document.getElementById('previewError');

        // Limpiar todo
        img.src = '';
        pdf.src = '';
        img.style.display = 'none';
        pdf.style.display = 'none';
        if (loader) loader.style.display = 'none';
        if (errorEl) errorEl.style.display = 'none';

        modal.classList.remove('active');
    }
    window.cargarDocumentosEmpleado = function (id) {
        fetch(`${getBaseUrl()}/rrhh/empleados/${id}/documentos`, {
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
            .then(res => res.json())
            .then(resp => {
                if (!resp.success) {
                    Swal.fire('Error', 'Error Cargando documentos', 'error');
                    return;
                }
                abrirListaDocumentos(resp.documentos);
            })
            .catch(err => {
                console.error(err);
                Swal.fire('Error', 'Error en servidor', 'error');
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
            const empleadoId = btnEditar.dataset.id;
            // Solo modal de empleados: otras vistas reutilizan .btn-editar sin data-id
            if (!empleadoId) return;
            e.preventDefault();
            e.stopPropagation();

            abrirModalEditarEmpleado(empleadoId);
            return
        }
    })
    window.abrirModalEditarEmpleado = function (id) {
        fetch(`${getBaseUrl()}/rrhh/empleados/${id}/json`, {
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
            .then(res => {
                if (!res.ok) {
                    return res.text().then(text => { throw new Error('HTTP ' + res.status + ': ' + text.substring(0, 200)); });
                }
                return res.json();
            })
            .then(resp => {
                if (!resp.success) {
                    Swal.fire('Error', 'Error del servidor: ' + (resp.error || 'No se pudo cargar el empleado'), 'error');
                    return;
                }
                const emp = resp.empleado

                // --- Helper: asignar valor a un <select> con Select2 ---
                // Select2 no detecta cambios en .value nativo; hay que usar
                // jQuery .val().trigger('change') para que el widget se actualice.
                function setSelect(id, valor) {
                    const el = document.getElementById(id);
                    if (!el) return;
                    const val = valor || '';
                    if ($(el).data('select2')) {
                        $(el).val(val).trigger('change');
                    } else {
                        el.value = val;
                    }
                }

                // --- Helper: asignar valor a un <input> ---
                // Usar != null para no tratar 0 como vacío
                function setInput(id, valor) {
                    const el = document.getElementById(id);
                    if (el) el.value = valor != null ? valor : '';
                }

                // === DATOS PERSONALES ===
                setSelect('tipo_identificacion', emp.tipo_identificacion);
                setInput('identificacion', emp.identificacion);
                setInput('nombres', emp.nombres);
                setInput('apellidos', emp.apellidos);
                setSelect('cedula_expedida_en', emp.cedula_expedida_en);
                setSelect('sexo', emp.sexo);
                setInput('fecha_nacimiento', emp.fecha_nacimiento);
                setSelect('lugar_nacimiento', emp.lugar_nacimiento);
                setInput('edad', emp.edad);
                setSelect('estado_civil_id', emp.estado_civil_id);
                setSelect('grupo_sanguineo_id', emp.grupo_sanguineo_id);
                setInput('numero_hijos', emp.numero_hijos);

                // === CONTACTO ===
                setInput('direccion', emp.direccion);
                setSelect('barrio', emp.barrio_id);
                setInput('barrio2', emp.barrio2 || '');
                setInput('localidad_id', emp.localidad);
                setSelect('estrato', emp.estrato);
                setInput('telefono_fijo', emp.telefono_fijo);
                setInput('celular', emp.celular);
                setInput('correo', emp.correo);
                setInput('contacto_emergencia', emp.contacto_emergencia);
                setInput('telefono_emergencia', emp.telefono_emergencia);
                setInput('parentesco', emp.parentesco);

                // === SEGURIDAD SOCIAL ===
                setSelect('eps_id', emp.eps_id);
                setSelect('afp_id', emp.afp_id);
                setSelect('cesantias_id', emp.cesantias_id);
                setSelect('ccf_id', emp.ccf_id);
                setSelect('arl_id', emp.arl_id);

                // === INFORMACIÓN LABORAL ===
                setSelect('tipo_contrato_id', emp.tipo_contrato_id);
                setSelect('cargo_id', emp.cargo_id);
                setSelect('jornada', emp.jornada);
                setSelect('sede', emp.sede);
                setInput('antiguedad', emp.antiguedad_texto || (emp.antiguedad ? emp.antiguedad + ' Años' : ''));
                setInput('salario_basico', window.formatearMoneda(emp.salario_basico, false));
                setInput('factor_no_salarial', window.formatearMoneda(emp.factor_no_salarial, false));
                setInput('numero_cuenta', emp.numero_cuenta);
                setSelect('banco', emp.banco);
                setSelect('grupo_nomina_id', emp.grupo_nomina_id);
                setSelect('sgi_rol_id', emp.sgi_rol_id || '');

                // === INFORMACIÓN EDUCATIVA ===
                setSelect('nivel_escolaridad_id', emp.nivel_escolaridad_id);
                setInput('programa_academico', emp.programa_academico);
                setSelect('estudia_actualmente', emp.estudia_actualmente);
                setInput('nombre_programa_actual', emp.nombre_programa_actual);

                const modalTitulo = document.getElementById('modalEmpleadoTitulo');
                if (modalTitulo) {
                    modalTitulo.innerHTML = '<i class="fa-solid fa-user-pen"></i> Editar Empleado';
                }

                document.getElementById("form_Empleado").dataset.editId = id;

                document.getElementById("btnGuardar").textContent = "Actualizar";

                // Actualizar foto preview con la foto actual del empleado
                const fp = document.getElementById('fotoPreview');
                if (fp) {
                    fp.src = emp.foto_path
                        ? (getBaseUrl() + '/' + emp.foto_path.replace(/\\/g, '/'))
                        : getBaseUrl() + '/static/imgs/user.png';
                }

                // Actualizar preview de cédula
                actualizarCedulaPreview(emp.cedula_path);

                abrirModalEmpleado();
            })
            .catch(err => {
                console.error(err);
                Swal.fire('Error', 'Error cargando empleado: ' + (err.message || 'Error desconocido'), 'error');
            });
    };

    window.actualizarFilaEmpleado = function (emp) {
        const filaPrincipal = document.querySelector(`.fila-principal[data-id="${emp.id}"]`);

        if (!filaPrincipal) return;

        // Helper function para actualizar segura (solo texto, no HTML)
        const actualizar = (selector, valor) => {
            const elem = filaPrincipal.querySelector(selector);
            if (elem) elem.textContent = valor || '';
        };

        actualizar('[data-column="tipo_doc"]', emp.tipo_doc_nombre);
        actualizar('[data-column="identificacion"]', emp.identificacion);
        // No usar actualizar() en nombres_y_apellidos porque destruiría el avatar HTML
        const nameSpan = filaPrincipal.querySelector('.emp-name-cell span');
        if (nameSpan) nameSpan.textContent = emp.apellidos + ' ' + emp.nombres;
        actualizar('[data-column="correo"]', emp.correo);
        actualizar('[data-column="cargo_id"]', emp.cargo_id);
        actualizar('[data-column="tipo_contrato_id"]', emp.tipo_contrato_id);

        // Actualizar foto en thumbnail
        const thumbImg = filaPrincipal.querySelector('.emp-photo-thumb');
        if (thumbImg) {
            thumbImg.src = emp.foto_path
                ? (getBaseUrl() + '/' + emp.foto_path.replace(/\\/g, '/'))
                : getBaseUrl() + '/static/imgs/user.png';
            thumbImg.onerror = function() { this.onerror = null; this.src = getBaseUrl() + '/static/imgs/user.png'; };
        }

        // Actualizar botones de previsualización de cédula y foto
        const btnCedula = filaPrincipal.querySelector('.btn-preview[data-tipo="cedula"]');
        if (btnCedula) {
            const url = emp.cedula_path ? emp.cedula_path.replace(/\\/g, '/') : '';
            btnCedula.dataset.url = url;
            // Actualizar indicador file-dot
            const dot = btnCedula.querySelector('.file-dot');
            if (emp.cedula_path) {
                if (!dot) btnCedula.insertAdjacentHTML('beforeend', '<span class="file-dot"></span>');
            } else {
                if (dot) dot.remove();
            }
        }
        const btnFoto = filaPrincipal.querySelector('.btn-preview[data-tipo="foto"]');
        if (btnFoto) {
            const url = emp.foto_path ? emp.foto_path.replace(/\\/g, '/') : '';
            btnFoto.dataset.url = url;
            const dot = btnFoto.querySelector('.file-dot');
            if (emp.foto_path) {
                if (!dot) btnFoto.insertAdjacentHTML('beforeend', '<span class="file-dot"></span>');
            } else {
                if (dot) dot.remove();
            }
        }

        const filaDetalles = filaPrincipal.nextElementSibling;
        if (filaDetalles && filaDetalles.classList.contains('fila-detalles')) {
            // Helper function para actualizar detalles
            const actualizarDetalle = (selector, valor) => {
                const elem = filaDetalles.querySelector(selector);
                if (elem) elem.textContent = valor || '';
            };

            // Actualizar foto en detalle (Personales tab)
            const detailImg = filaDetalles.querySelector('.emp-photo-detail');
            if (detailImg) {
                detailImg.src = emp.foto_path
                    ? (getBaseUrl() + '/' + emp.foto_path.replace(/\\/g, '/'))
                    : getBaseUrl() + '/static/imgs/user.png';
                detailImg.onerror = function() { this.onerror = null; this.src = getBaseUrl() + '/static/imgs/user.png'; };
            }

            actualizarDetalle('[data-column="tipo_doc_nombre"]', emp.tipo_doc_nombre);
            actualizarDetalle('[data-column="cedula_expedida_en"]', emp.cedula_expedida_en);
            actualizarDetalle('[data-column="sexo"]', emp.sexo);
            actualizarDetalle('[data-column="fecha_nacimiento"]', emp.fecha_nacimiento);
            actualizarDetalle('[data-column="lugar_nacimiento"]', emp.lugar_nacimiento);
            actualizarDetalle('[data-column="edad"]', emp.edad);
            actualizarDetalle('[data-column="estado_civil_id"]', emp.estado_civil_id);
            actualizarDetalle('[data-column="grupo_sanguineo_id"]', emp.grupo_sanguineo_id);
            actualizarDetalle('[data-column="numero_hijos"]', emp.numero_hijos);
            actualizarDetalle('[data-column="direccion"]', emp.direccion);
            actualizarDetalle('[data-column="barrio"]', emp.barrio);
            actualizarDetalle('[data-column="barrio2"]', emp.barrio2);
            actualizarDetalle('[data-column="localidad"]', emp.localidad);
            actualizarDetalle('[data-column="estrato"]', emp.estrato);
            actualizarDetalle('[data-column="telefono_fijo"]', emp.telefono_fijo);
            actualizarDetalle('[data-column="celular"]', emp.celular);
            actualizarDetalle('[data-column="contacto_emergencia"]', emp.contacto_emergencia);
            actualizarDetalle('[data-column="telefono_emergencia"]', emp.telefono_emergencia);
            actualizarDetalle('[data-column="parentesco"]', emp.parentesco);
            actualizarDetalle('[data-column="eps_id"]', emp.eps_id);
            actualizarDetalle('[data-column="afp_id"]', emp.afp_id);
            actualizarDetalle('[data-column="cesantias_id"]', emp.cesantias_id);
            actualizarDetalle('[data-column="ccf_id"]', emp.ccf_id);
            actualizarDetalle('[data-column="arl_id"]', emp.arl_id);
            actualizarDetalle('[data-column="jornada"]', emp.jornada);
            actualizarDetalle('[data-column="sede"]', emp.sede);
            actualizarDetalle('[data-column="fecha_ingreso"]', emp.fecha_ingreso);
            actualizarDetalle('[data-column="antiguedad"]', emp.antiguedad_texto || (emp.antiguedad ? emp.antiguedad + ' Años' : ''));
            actualizarDetalle('[data-column="salario_basico"]', window.formatearMoneda(emp.salario_basico));
            actualizarDetalle('[data-column="factor_no_salarial"]', window.formatearMoneda(emp.factor_no_salarial));
            actualizarDetalle('[data-column="numero_cuenta"]', emp.numero_cuenta);
            actualizarDetalle('[data-column="banco"]', emp.banco);
            actualizarDetalle('[data-column="grupo_nomina_id"]', emp.grupo_nomina_id);
            actualizarDetalle('[data-column="sgi_rol"]', emp.sgi_rol || 'Sin acceso');
            actualizarDetalle('[data-column="nivel_escolaridad_id"]', emp.nivel_escolaridad_id);
            actualizarDetalle('[data-column="programa_academico"]', emp.programa_academico);
            actualizarDetalle('[data-column="estudia_actualmente"]', emp.estudia_actualmente);
            actualizarDetalle('[data-column="nombre_programa_actual"]', emp.nombre_programa_actual);
        }

        // Re-aplicar filtros activos (búsqueda / tipo de contrato) tras actualizar la fila
        if (window.aplicarFiltrosEmpleados) window.aplicarFiltrosEmpleados();
    };

    //------------------------------------------------------
    //----------------- DESACTIVAR EMPLEADO ----------------
    //------------------------------------------------------
    let empleadoRetiroId = null;
    document.addEventListener("click", function (e) {
        const btnEliminar = e.target.closest(".btn-eliminar");
        if (!btnEliminar) return;
        if (!btnEliminar.dataset.id) return;
        e.preventDefault();
        e.stopPropagation();
        empleadoRetiroId = btnEliminar.dataset.id;
        document.getElementById("fecha_retiro").value = "";
        document.getElementById("modalRetiro").classList.add("active");
    });
    window.guardarFechaRetiro = function () {
        const btn = document.getElementById('btnGuardarRetiro');
        const motivoRetiro = document.getElementById("motivo_retiro").value;
        if (!motivoRetiro) {
            Swal.fire('Advertencia', 'Por favor ingrese un motivo de retiro', 'warning');
            return;
        }
        const fechaRetiro = document.getElementById("fecha_retiro").value;
        if (!fechaRetiro) {
            Swal.fire('Advertencia', 'Por favor ingrese una fecha de retiro', 'warning');
            return;
        }
        btn.disabled = true;
        btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Guardando...';
        fetch(`${getBaseUrl()}/rrhh/empleados/retirar/${empleadoRetiroId}`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ fecha_retiro: fechaRetiro, motivo_retiro: motivoRetiro })
        })
            .then(res => res.json())
            .then(resp => {
                if (!resp.success) {
                    btn.disabled = false;
                    btn.innerHTML = '<i class="fa-solid fa-check"></i> Guardar';
                    Swal.fire('Error', 'error: ' + resp.error, 'error');
                    return;
                }
                Swal.fire('Éxito', 'Empleado retirado correctamente', 'success');
                document.getElementById("modalRetiro").classList.remove("active");
                location.reload();
            })
            .catch(err => {
                console.error(err);
                btn.disabled = false;
                btn.innerHTML = '<i class="fa-solid fa-check"></i> Guardar';
                Swal.fire('Error', 'Error en el servidor', 'error');
            });
    }

    window.cerrarModalConAnimacion = function (modalEl) {
        if (!modalEl || modalEl.classList.contains('closing')) return;
        modalEl.classList.add('closing');
        setTimeout(() => {
            modalEl.classList.remove('active', 'closing');
        }, 200);
    };

    window.cerrarModalRetiro = function () {
        cerrarModalConAnimacion(document.getElementById('modalRetiro'));
    }

    //------------------------------------------------------
    //------------------ ACTIVAR EMPLEADO ------------------
    //------------------------------------------------------
    let empleadoActivarId = null;
    document.addEventListener("click", function (e) {
        const btnActivar = e.target.closest(".btn-activar");
        if (!btnActivar) return;
        if (!btnActivar.dataset.id) return;
        e.preventDefault();
        e.stopPropagation();
        empleadoActivarId = btnActivar.dataset.id;
        document.getElementById("fecha_ingreso").value = "";
        document.getElementById("modalIngreso").classList.add("active");
    });
    window.guardarFechaIngreso = function () {
        const btn = document.getElementById('btnGuardarIngreso');
        const fechaIngreso = document.getElementById("fecha_ingreso").value;
        const salario_basico = document.getElementById("salario_basico_ingreso").value;
        const factor_no_salarial = document.getElementById("factor_no_salarial_ingreso").value;
        const tipoContrato = document.getElementById('tipo_contrato').value;
        if (!salario_basico) {
            Swal.fire('Advertencia', 'Por favor ingrese un salario básico', 'warning');
            return;
        }
        if (!fechaIngreso) {
            Swal.fire('Advertencia', 'Por favor ingrese una fecha de ingreso', 'warning');
            return;
        }
        btn.disabled = true;
        btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Guardando...';
        fetch(`${getBaseUrl()}/rrhh/empleados/activar/${empleadoActivarId}`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ fecha_ingreso: fechaIngreso, salario_basico: salario_basico, factor_no_salarial: factor_no_salarial, tipo_contrato: tipoContrato })
        })
            .then(res => res.json())
            .then(resp => {
                if (!resp.success) {
                    btn.disabled = false;
                    btn.innerHTML = '<i class="fa-solid fa-check"></i> Guardar';
                    Swal.fire('Error', 'error: ' + resp.error, 'error');
                    return;
                }
                Swal.fire('Éxito', 'Empleado activado correctamente', 'success');
                document.getElementById("modalIngreso").classList.remove("active");
                location.reload();
            })
            .catch(err => {
                console.error(err);
                btn.disabled = false;
                btn.innerHTML = '<i class="fa-solid fa-check"></i> Guardar';
                Swal.fire('Error', 'Error en el servidor', 'error');
            });
    }

    window.cerrarModalIngreso = function () {
        cerrarModalConAnimacion(document.getElementById('modalIngreso'));
    }

    //------------------------------------------------------
    //------------ ELIMINAR EMPLEADO (DEFINITIVO) ----------
    //------------------------------------------------------
    // Requiere la contraseña del usuario con la sesión abierta
    document.addEventListener("click", function (e) {
        const btnEliminar = e.target.closest(".btn-eliminar-def");
        if (!btnEliminar || !btnEliminar.dataset.id) return;
        e.preventDefault();
        e.stopPropagation();
        const empleadoId = btnEliminar.dataset.id;

        Swal.fire({
            title: '¿Eliminar definitivamente?',
            html: 'Esta acción <b>no se puede deshacer</b>.<br>' +
                'Se eliminarán el empleado, sus contratos, Otrosí, documentos y su historial.<br><br>' +
                'Ingresa tu <b>contraseña</b> para confirmar:',
            icon: 'warning',
            input: 'password',
            inputPlaceholder: 'Tu contraseña',
            inputAttributes: { autocapitalize: 'off', autocomplete: 'off' },
            showCancelButton: true,
            confirmButtonText: 'Eliminar definitivamente',
            confirmButtonColor: '#dc3545',
            cancelButtonText: 'Cancelar',
            showLoaderOnConfirm: true,
            preConfirm: (password) => {
                if (!password) {
                    Swal.showValidationMessage('Debes ingresar tu contraseña');
                    return false;
                }
                return fetch(`${getBaseUrl()}/rrhh/empleados/eliminar/${empleadoId}`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ password: password })
                })
                    .then(res => res.json())
                    .then(resp => {
                        if (!resp.success) {
                            Swal.showValidationMessage(resp.error || 'No se pudo eliminar el empleado');
                            return false;
                        }
                        return resp;
                    })
                    .catch(() => {
                        Swal.showValidationMessage('Error en el servidor');
                    });
            }
        }).then((result) => {
            if (result.isConfirmed) {
                Swal.fire('Eliminado', 'Empleado eliminado definitivamente', 'success');
                location.reload();
            }
        });
    });


    //------------------------------------------------------
    //---------- SELECT2 PARA TODOS LOS SELECT DEL MODAL -------
    //------------------------------------------------------
    let _select2Retries = 0;
    const _SELECT2_MAX_RETRIES = 20;
    function initSelect2Modal() {
        if (_select2Retries >= _SELECT2_MAX_RETRIES) {
            console.warn('Select2 no disponible después de ' + _SELECT2_MAX_RETRIES + ' intentos');
            return;
        }
        _select2Retries++;
        if (typeof $ !== 'undefined' && $.fn && $.fn.select2) {
            // Seleccionar todos los <select> dentro del modal del empleado,
            // excepto los que tengan la clase 'no-select2' (por si acaso uno
            // no debe ser convertido).
            $('#modalEmpleado select').not('.no-select2').each(function () {
                const $sel = $(this);
                // Evitar inicializar dos veces
                if ($sel.data('select2')) return;
                $sel.select2({
                    placeholder: $sel.find('option[value=""]').text() || 'Buscar...',
                    allowClear: true,
                    width: '100%',
                    dropdownParent: $('#modalEmpleado'),
                    language: 'es'
                });
            });
            console.log('Select2 inicializado en todos los selects del modal');
        } else {
            console.warn('Select2 no disponible, reintentando (' + _select2Retries + '/' + _SELECT2_MAX_RETRIES + ')...');
            setTimeout(initSelect2Modal, 500);
        }
    }
    initSelect2Modal();


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
            fetch(`${getBaseUrl()}/rrhh/empleados/${empleadoId}/contratos`, {
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            })
                .then(res => res.json())
                .then(resp => {
                    if (!resp.success) {
                        Swal.fire('Error', 'Error cargando contratos', 'error');
                        return;
                    }                        const tbody = document.getElementById('tabla_contratos_empleado_body');
                    tbody.innerHTML = '';
                    resp.contratos.forEach(contrato => {

                        //crea fila princial
                        const trPrincipal = document.createElement('tr');
                        trPrincipal.classList.add('fila-principal-contrato');
                        
                        const tfin = (contrato.fecha_finalizacion === null || contrato.fecha_finalizacion === '')
                                ? null : contrato.fecha_finalizacion;
                        const estaActivo = contrato.fecha_finalizacion === null || contrato.fecha_finalizacion === '';
                        const motivo = contrato.motivo || 'N/A';
                        const estadoBadge = estaActivo
                            ? '<span class="badge-activo">● Activo</span>'
                            : '<span class="badge-finalizado">● Finalizado</span>';
                        const salarioFormateado = contrato.salario_basico
                            ? window.formatearMoneda(contrato.salario_basico)
                            : '—';
                        const factorFormateado = contrato.factor_no_salarial
                            ? window.formatearMoneda(contrato.factor_no_salarial)
                            : '—';
                        trPrincipal.innerHTML = `
                                <td data-column="codigo"><strong>${contrato.n_consecutivo}</strong></td>
                                <td data-column="tipo_contrato">${contrato.tipo_contrato}</td>
                                <td data-column="fecha_inicio">${contrato.fecha_ingreso}</td>
                                <td data-column="fecha_fin">${tfin || '—'}</td>
                                <td data-column="salario_basico">${salarioFormateado}</td>
                                <td data-column="factor_no_salarial">${factorFormateado}</td>
                                <td data-column="motivo">${motivo}</td>
                                <td data-column="estado">${estadoBadge}</td>
                            `;
                        tbody.appendChild(trPrincipal);

                        //crea fila detalles (otrosi)
                        const trDetalle = document.createElement('tr');
                        trDetalle.classList.add('fila-detalles-contrato');
                        trDetalle.style.display = 'none';

                        let otrosiHTML = '';
                        if(contrato.otrosi && contrato.otrosi.length > 0){
                            otrosiHTML = `
                                <div class="otrosi-card">
                                    <div class="otrosi-card-header">
                                        <i class="fa-solid fa-paperclip"></i>
                                        <strong>Otrosí realizados a este contrato (${contrato.otrosi.length})</strong>
                                    </div>
                                    <div class="otrosi-card-body">
                                        ${contrato.otrosi.map((o, idx) => `
                                            <div class="otrosi-item">
                                                <div class="otrosi-item-icon">
                                                    <i class="fa-solid fa-file-pen"></i>
                                                </div>
                                                <div class="otrosi-item-content">
                                                    <span class="otrosi-item-type">${o.tipo_otrosi} - ${idx + 1}</span>
                                                    <span class="otrosi-item-date"><i class="fa-regular fa-calendar"></i> ${o.fecha_inicio || '—'} <i class="fa-solid fa-arrow-right"></i> ${o.fecha_fin || '—'}</span>
                                                    ${o.descripcion ? `<span class="otrosi-item-desc">${o.descripcion}</span>` : ''}
                                                </div>
                                            </div>
                                        `).join('')}
                                    </div>
                                </div>
                            `;
                        } else {
                            otrosiHTML = `
                                <div class="otrosi-card otrosi-empty">
                                    <div class="otrosi-card-body">
                                        <i class="fa-regular fa-circle-check fs-icon icon-green-500"></i>
                                        <span class="text-slate-500">Este contrato no tiene Otrosí registrados.</span>
                                    </div>
                                </div>
                            `;
                        }
                        trDetalle.innerHTML = `<td colspan="8">${otrosiHTML}</td>`;
                        tbody.appendChild(trDetalle);
                    });
                })
                .catch(err => {
                    Swal.fire('Error', 'Error en el servidor', 'error');
                });
        }
    });
    window.cerrarModalContratos = function () {
        const modal = document.getElementById('modalContratos');
        cerrarModalConAnimacion(modal);
        // Limpiar tabla al cerrar
        const tbody = document.getElementById('tabla_contratos_empleado_body');
        if (tbody) tbody.innerHTML = '';
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
        const titulo = document.getElementById('modalImportarTitulo');
        const labels = {
            'crear': 'Cargar Empleados Masivamente',
            'actualizar': 'Actualizar Empleados Masivamente',
            'contratos': 'Importar Contratos Masivamente',
            'rol_sgi': 'Asignar Rol SGI Masivamente'
        };
        if (titulo) {
            titulo.textContent = labels[modoModal] || 'Cargar Empleados Masivamente';
        }
        modal.classList.add('active');
    };

    /**
     * Crea o actualiza la barra de progreso en el modal de importación.
     */
    function actualizarProgreso(pct, label, variant) {
        const container = document.getElementById('importProgressContainer');
        const fill = document.getElementById('importProgressFill');
        const pctEl = document.getElementById('importProgressPct');
        const labelEl = document.getElementById('importProgressLabel');

        if (!container || !fill || !pctEl || !labelEl) return;

        container.classList.add('show');
        fill.style.width = Math.min(pct, 100) + '%';
        pctEl.textContent = Math.min(pct, 100) + '%';
        labelEl.innerHTML = label;

        // Variantes de color
        fill.classList.remove('complete', 'error');
        if (variant === 'complete') fill.classList.add('complete');
        if (variant === 'error') fill.classList.add('error');
    }

    window.cerrarModalImportar = function () {
        const modal = document.getElementById('modalImportar');
        cerrarModalConAnimacion(modal);
        // Limpiar después de que termine la animación (200ms)
        setTimeout(() => {
            document.getElementById('formImportarExcel').reset();
            const res = document.getElementById('resultadoImportacion');
            res.style.display = 'none';
            res.innerHTML = '';
            const container = document.getElementById('importProgressContainer');
            if (container) container.classList.remove('show');
        }, 200);
    };

    const COLUMNAS_REQUERIDAS = [
        'IDENTIFICACION',
        'NOMBRES',
        'APELLIDOS',
        'CEDULA_EXPEDIDA_EN',
        'SEXO (M/F)',
        'FECHA_NACIMIENTO (AAAA-MM-DD)',
        'LUGAR_NACIMIENTO',
        'DIRECCION',
        'CIUDAD_BARRIO',
        'CELULAR',
        'CORREO',
        'CONTACTO_EMERGENCIA',
        'TELEFONO_EMERGENCIA',
        'PARENTESCO'
    ];

    /**
     * Valida las columnas del Excel client-side usando SheetJS (XLSX).
     * Retorna { valido: bool, mensaje: string, columnasFaltantes: string[] }
     */
    function validarEstructuraExcel(file) {
        return new Promise((resolve) => {
            // Verificar que SheetJS haya cargado
            if (typeof XLSX === 'undefined') {
                resolve({ valido: false, mensaje: 'La librería de lectura de Excel aún no ha cargado. Espera unos segundos e intenta de nuevo.', columnasFaltantes: [] });
                return;
            }
            const reader = new FileReader();
            reader.onload = function (e) {
                try {
                    const data = new Uint8Array(e.target.result);
                    const workbook = XLSX.read(data, { type: 'array' });
                    const firstSheet = workbook.Sheets[workbook.SheetNames[0]];
                    const json = XLSX.utils.sheet_to_json(firstSheet, { header: 1 });

                    if (json.length === 0) {
                        resolve({ valido: false, mensaje: 'El archivo Excel está vacío.', columnasFaltantes: [] });
                        return;
                    }

                    const headers = json[0].map(h => String(h || '').trim().toUpperCase());
                    const missing = COLUMNAS_REQUERIDAS.filter(col => !headers.includes(col));

                    if (missing.length > 0) {
                        resolve({ valido: false, mensaje: `Faltan ${missing.length} columna(s) requerida(s).`, columnasFaltantes: missing });
                    } else {
                        resolve({ valido: true, mensaje: '', columnasFaltantes: [] });
                    }
                } catch (err) {
                    console.error('Error al leer Excel:', err);
                    resolve({ valido: false, mensaje: 'Error al leer el archivo: ' + err.message, columnasFaltantes: [] });
                }
            };
            reader.onerror = function () {
                resolve({ valido: false, mensaje: 'Error al leer el archivo.', columnasFaltantes: [] });
            };
            reader.readAsArrayBuffer(file);
        });
    }

    const formImportar = document.getElementById('formImportarExcel');

    if (formImportar) {
        formImportar.addEventListener('submit', async function (e) {
            e.preventDefault();

            const endpointMap = {
                'crear': `${getBaseUrl()}/rrhh/empleados/importar_empleados`,
                'actualizar': `${getBaseUrl()}/rrhh/empleados/actualizar_empleados`,
                'contratos': `${getBaseUrl()}/rrhh/empleados/importar_contratos`,
                'rol_sgi': `${getBaseUrl()}/rrhh/empleados/asignar_rol_sgi`,
            };
            const endpoint = endpointMap[modoModal] || `${getBaseUrl()}/rrhh/empleados/importar_empleados`;
            const fileInput = document.getElementById('archivo_excel');
            const btnCargar = document.getElementById('btnCargarExcel');
            const resultadoDiv = document.getElementById('resultadoImportacion');

            // 1. Validar que haya un archivo
            if (fileInput.files.length === 0) {
                Swal.fire('Advertencia', 'Por favor, seleccione un archivo Excel.', 'warning');
                return;
            }

            // 2. Mostrar barra de progreso — Fase 0: Inicio
            resultadoDiv.className = 'import-result show';
            resultadoDiv.innerHTML = `
                <div class="import-progress-container show" id="importProgressContainer">
                    <div class="import-progress-bar-track">
                        <div class="import-progress-bar-fill" id="importProgressFill" style="width: 0%"></div>
                    </div>
                    <div class="import-progress-info">
                        <span class="import-progress-label" id="importProgressLabel">
                            <i class="fa-solid fa-spinner"></i> Iniciando...
                        </span>
                        <span class="import-progress-pct" id="importProgressPct">0%</span>
                    </div>
                </div>
            `;

            btnCargar.disabled = true;
            btnCargar.textContent = "Validando archivo...";

            // 3. Fase 1: Validación client-side (0% → 15%)
            actualizarProgreso(5, '<i class="fa-solid fa-spinner"></i> Validando estructura del archivo...');
            await new Promise(r => setTimeout(r, 200));

            // Saltar validación de columnas para contratos/rol_sgi (tienen estructura distinta)
            if (modoModal === 'contratos' || modoModal === 'rol_sgi') {
                // Pasar directo a la subida
                actualizarProgreso(15, '<i class="fa-solid fa-spinner"></i> Estructura válida');
            } else {
                actualizarProgreso(10, '<i class="fa-solid fa-spinner"></i> Validando columnas requeridas...');

                const validacion = await validarEstructuraExcel(fileInput.files[0]);

                if (!validacion.valido) {
                    actualizarProgreso(100, '<i class="fa-solid fa-circle-xmark"></i> Validación fallida', 'error');
                    // Pequeña pausa para que se vea el 100% rojo
                    await new Promise(r => setTimeout(r, 400));
                    resultadoDiv.className = 'import-result show import-error';
                    let html = `<div class="import-result-summary">❌ ${validacion.mensaje}</div>`;

                    if (validacion.columnasFaltantes.length > 0) {
                        html += `<div class="import-column-error-list">`;
                        html += `<div class="import-column-error-header"><i class="fa-solid fa-list"></i> Columnas faltantes:</div>`;
                        validacion.columnasFaltantes.forEach(col => {
                            html += `<div class="import-column-error-item">
                                <i class="fa-solid fa-circle-xmark"></i>
                                <span>${col}</span>
                            </div>`;
                        });
                        html += `<div class="import-column-hint">
                            <i class="fa-solid fa-download"></i>
                            <a href="${getBaseUrl()}/rrhh/descargar_plantilla_excel">Descarga la plantilla oficial</a> para ver la estructura correcta.
                        </div>`;
                        html += `</div>`;
                    }

                    resultadoDiv.innerHTML = html;
                    btnCargar.disabled = false;
                    btnCargar.textContent = "Procesar Carga";
                    return;
                }
            }

            // 4. Fase 2: Preparar envío (15% → 30%)
            actualizarProgreso(15, '<i class="fa-solid fa-spinner"></i> Preparando datos para enviar...');
            await new Promise(r => setTimeout(r, 150));

            const formData = new FormData();
            formData.append('file', fileInput.files[0]);

            actualizarProgreso(20, '<i class="fa-solid fa-spinner"></i> Subiendo archivo al servidor...');

            // 5. Fase 3: Subida — simular progreso mientras fetch se ejecuta (20% → 70%)
            let progressInterval = null;
            let uploadProgress = 20;
            progressInterval = setInterval(() => {
                // Subir progreso simulado hasta 70%
                if (uploadProgress < 70) {
                    uploadProgress += Math.random() * 4 + 1;
                    if (uploadProgress > 70) uploadProgress = 70;
                    actualizarProgreso(uploadProgress, '<i class="fa-solid fa-spinner"></i> Subiendo archivo al servidor...');
                }
            }, 400);

            // 6. Enviar al servidor
            let response;
            try {
                response = await fetch(endpoint, {
                    method: 'POST',
                    body: formData
                });
            } catch (err) {
                clearInterval(progressInterval);
                actualizarProgreso(100, '<i class="fa-solid fa-circle-xmark"></i> Error de conexión', 'error');
                await new Promise(r => setTimeout(r, 400));
                btnCargar.disabled = false;
                btnCargar.textContent = "Procesar Carga";
                resultadoDiv.className = 'import-result show import-error';
                resultadoDiv.innerHTML = `<div class="import-result-summary">❌ Error de conexión: ${err.message}</div>`;
                return;
            }

            // Limpiar el intervalo de progreso simulado
            clearInterval(progressInterval);

            // 7. Fase 4: Procesando respuesta (70% → 90%)
            actualizarProgreso(75, '<i class="fa-solid fa-spinner"></i> Procesando respuesta del servidor...');

            let data;
            try {
                data = await response.json();
            } catch (err) {
                actualizarProgreso(100, '<i class="fa-solid fa-circle-xmark"></i> Error al leer respuesta', 'error');
                await new Promise(r => setTimeout(r, 400));
                btnCargar.disabled = false;
                btnCargar.textContent = "Procesar Carga";
                resultadoDiv.className = 'import-result show import-error';
                resultadoDiv.innerHTML = `<div class="import-result-summary">❌ Error al procesar la respuesta del servidor.</div>`;
                return;
            }

            actualizarProgreso(85, '<i class="fa-solid fa-spinner"></i> Generando reporte...');
            await new Promise(r => setTimeout(r, 300));

            // 8. Fase 5: Mostrar resultado (90% → 100%)
            if (response.status === 200 && data.success) {
                actualizarProgreso(95, '<i class="fa-solid fa-spinner"></i> Finalizando...');
                await new Promise(r => setTimeout(r, 200));
                actualizarProgreso(100, '<i class="fa-solid fa-check-circle"></i> Proceso completado', 'complete');
                await new Promise(r => setTimeout(r, 500));

                const cantidad = data.insertados || data.actualizados || data.procesados || 0;
                const total = data.total_filas || 0;
                const erroresCount = data.errores_count || 0;
                const accionLabels = {
                    'crear': 'importado',
                    'actualizar': 'actualizado',
                    'contratos': 'procesado',
                    'rol_sgi': 'procesado'
                };
                const accion = accionLabels[modoModal] || 'importado';

                if (erroresCount > 0) {
                    resultadoDiv.className = 'import-result show import-warning';
                    let html = `
                        <div class="import-result-summary">
                            ⚠️ Proceso completado con errores<br>
                            <span class="count-ok">✅ ${cantidad}</span> de ${total} empleados ${accion}ron correctamente.<br>
                            <span class="count-err">❌ ${erroresCount}</span> empleados con errores.
                        </div>
                    `;
                    if (data.errores && data.errores.length > 0) {
                        html += `<div class="import-error-list">`;
                        data.errores.slice(0, 10).forEach(err => {
                            const ident = err['IDENTIFICACION'] || '?';
                            const nombre = err['NOMBRES'] || '';
                            html += `<div class="import-error-item">
                                <span class="import-error-fila">Fila ${err['FILA EXCEL']}</span>
                                <span class="import-error-ident">${ident}${nombre ? ' — ' + nombre : ''}</span>
                                <span class="import-error-msg">${err['ERROR']}</span>
                            </div>`;
                        });
                        if (data.errores.length > 10) {
                            html += `<div class="import-error-more">... y ${data.errores.length - 10} errores más</div>`;
                        }
                        html += `</div>`;
                    }
                    if (data.error_excel_url) {
                        html += `<a href="${data.error_excel_url}" class="import-error-download" download>
                            <i class="fa-solid fa-file-excel"></i> Descargar Excel con errores
                        </a>`;
                    }
                    resultadoDiv.innerHTML = html;
                    btnCargar.disabled = false;
                    btnCargar.textContent = "Procesar Carga";
                } else {
                    resultadoDiv.className = 'import-result show import-success';
                    resultadoDiv.innerHTML = `<div class="import-result-summary">✅ ¡Éxito! Se ${accion}ron <strong>${cantidad}</strong> empleados correctamente.</div>`;
                    setTimeout(() => {
                        location.reload();
                    }, 2000);
                }
            } else {
                actualizarProgreso(100, '<i class="fa-solid fa-circle-xmark"></i> Error del servidor', 'error');
                await new Promise(r => setTimeout(r, 400));
                btnCargar.disabled = false;
                btnCargar.textContent = "Procesar Carga";
                resultadoDiv.className = 'import-result show import-error';
                resultadoDiv.innerHTML = `<div class="import-result-summary">❌ Error: ${data.error || 'Error desconocido'}</div>`;
            }
        });
    }

    //------------------------------------------------------
    //--------- ACCIONES MASIVAS PARA DOCUMENTOS ---------
    //------------------------------------------------------
    window.abrirModalZip = function () {
        document.getElementById('modalZip').classList.add('active');
    };

    window.cerrarModalZip = function () {
        const modal = document.getElementById('modalZip');
        cerrarModalConAnimacion(modal);
        setTimeout(() => {
            document.getElementById('formImportarZip').reset();
            const resDiv = document.getElementById('resultadoZip');
            resDiv.style.display = 'none';
            resDiv.className = 'zip-result';
            resDiv.innerHTML = '';
        }, 200);
    };

    document.getElementById('formImportarZip')?.addEventListener('submit', function (e) {
        e.preventDefault();
        const btn = document.getElementById('btnCargarZip');
        const resDiv = document.getElementById('resultadoZip');
        const formData = new FormData();
        formData.append('file', document.getElementById('archivo_zip').files[0]);

        btn.disabled = true;
        btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Procesando ZIP...';
        resDiv.className = 'zip-result show';
        resDiv.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Extrayendo y organizando archivos...';
        resDiv.style.color = '#475569';

        fetch(`${getBaseUrl()}/rrhh/empleados/importar_zip`, {
            method: 'POST',
            body: formData
        })
            .then(res => res.json().then(data => ({ status: res.status, data: data })))
            .then(({ status, data }) => {
                if (status === 200 && data.success) {
                    Swal.fire('Éxito', `¡Éxito! Se procesaron ${data.archivos} archivos.`, 'success');
                    location.reload();
                } else {
                    resDiv.className = 'zip-result show zip-error';
                    resDiv.innerHTML = `<i class="fa-solid fa-circle-xmark"></i> Error: ${data.error || 'Error desconocido'}`;
                    resDiv.style.color = '';
                    btn.disabled = false;
                    btn.innerHTML = '<i class="fa-solid fa-cloud-arrow-up"></i> Subir y Procesar';
                }
            })
            .catch(err => {
                console.error("Error en ZIP:", err);
                resDiv.className = 'zip-result show zip-error';
                resDiv.innerHTML = `<i class="fa-solid fa-circle-xmark"></i> Error crítico: ${err.message}`;
                resDiv.style.color = '';
                btn.disabled = false;
                btn.innerHTML = '<i class="fa-solid fa-cloud-arrow-up"></i> Subir y Procesar';
            });
    });

    //------------------------------------------------------
    //---------------- BUSCAR Y FILTRAR ---------------------
    //------------------------------------------------------
    //--- MAPA DE FILTROS AVANZADOS: id del select → columna de la fila detalle ---
    // El valor de cada select se compara (sin tildes, sin mayúsculas) con el texto
    // de la celda correspondiente dentro de la fila de detalles del empleado.
    const MAPA_FILTROS_AVANZADOS = {
        'filtroTipoContrato': 'tipo_contrato',
        'filtroCargo': 'cargo',
        'filtroSede': 'sede',
        'filtroEps': 'eps_id',
        'filtroArl': 'arl_id',
        'filtroAfp': 'afp_id',
        'filtroEstadoCivil': 'estado_civil_id',
        'filtroSexo': 'sexo',
        'filtroJornada': 'jornada',
        'filtroBanco': 'banco',
        'filtroGrupoNomina': 'grupo_nomina',
        'filtroNivelEscolaridad': 'nivel_escolaridad_id'
    };
    const IDS_FILTROS_MULTIPLES = Object.keys(MAPA_FILTROS_AVANZADOS);
    const FILTRO_MES_NACIMIENTO = 'filtroMesNacimiento';
    const IDS_FILTROS_AV = IDS_FILTROS_MULTIPLES.concat([FILTRO_MES_NACIMIENTO]);

    // Normaliza texto: minúsculas y sin tildes ("Medellín" == "medellin")
    function normalizarTexto(valor) {
        return String(valor || '')
            .toLowerCase()
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '');
    }

    // Compara el texto de una celda con los valores seleccionados del filtro.
    // La celda puede contener varios valores separados por coma (ej. varias
    // sedes: "Medellín, Rionegro"), por eso se compara token a token y de
    // forma EXACTA (sin tildes/mayúsculas) para evitar falsos positivos por
    // prefijos (ej. "Medellín" no debe coincidir con "Medellín Centro").
    function celdaCoincide(valorCelda, valores) {
        if (!valorCelda) return false;
        const tokens = valorCelda.split(/[,;|]+/).map(t => t.trim()).filter(t => t !== '');
        return valores.some(v => valorCelda === v || tokens.includes(v));
    }

    // Cuenta cuántos filtros avanzados tienen un valor seleccionado (para el badge)
    function contarFiltrosActivos() {
        let activos = 0;
        IDS_FILTROS_MULTIPLES.forEach(id => {
            const el = document.getElementById(id);
            if (el && ($(el).val() || []).length > 0) activos++;
        });
        const mesEl = document.getElementById(FILTRO_MES_NACIMIENTO);
        if (mesEl && mesEl.value) activos++;
        return activos;
    }

    window.aplicarFiltrosEmpleados = function () {
        const inputBusqueda = document.getElementById('inputBusquedaID');

        const filtroTexto = inputBusqueda ? inputBusqueda.value.toLowerCase().trim() : '';

        //--- Filtros avanzados: { columna: [valores normalizados] } ---
        const filtrosAv = {};
        IDS_FILTROS_MULTIPLES.forEach(id => {
            const el = document.getElementById(id);
            if (!el) return;
            const valores = ($(el).val() || [])
                .map(v => normalizarTexto(v))
                .filter(v => v !== '');
            if (valores.length > 0) {
                filtrosAv[MAPA_FILTROS_AVANZADOS[id]] = valores;
            }
        });
        // Mes de nacimiento ("02") — se compara con el texto dd/mm/yyyy o yyyy-mm-dd de la celda
        const mesNacSel = document.getElementById(FILTRO_MES_NACIMIENTO);
        const filtroMesNac = mesNacSel ? (mesNacSel.value || '') : '';

        // Persistir los filtros para conservarlos al recargar la página
        // tras una modificación (contrato, retiro, etc.)
        try {
            sessionStorage.setItem('rrhh_filtro_busqueda', inputBusqueda ? inputBusqueda.value : '');
            // El filtro de tipo de contrato ahora se guarda dentro de rrhh_filtro_avanzado
            sessionStorage.removeItem('rrhh_filtro_contratos');
            const guardadoAv = {};
            IDS_FILTROS_MULTIPLES.forEach(id => {
                const el = document.getElementById(id);
                if (el) guardadoAv[id] = $(el).val() || [];
            });
            guardadoAv[FILTRO_MES_NACIMIENTO] = filtroMesNac;
            sessionStorage.setItem('rrhh_filtro_avanzado', JSON.stringify(guardadoAv));
        } catch (e) { /* almacenamiento no disponible: el filtro no persiste */ }

        // Actualizar badge del botón "Filtros Avanzados"
        const badge = document.getElementById('badgeFiltrosAv');
        if (badge) {
            const n = contarFiltrosActivos();
            badge.textContent = n;
            badge.style.display = n > 0 ? 'inline-flex' : 'none';
        }

        const tbody = document.getElementById('tabla_lista_empleados_body');
        if (!tbody) return;
        const filasPrincipal = tbody.querySelectorAll('.fila-principal');

        let visibles = 0;

        filasPrincipal.forEach(filaPrincipal => {
            const celdaId = filaPrincipal.querySelector('[data-column="identificacion"]');
            const celdaNombre = filaPrincipal.querySelector('[data-column="nombres_y_apellidos"]');

            const textoID = celdaId ? celdaId.textContent.toLowerCase() : '';
            const textoNombre = celdaNombre ? celdaNombre.textContent.toLowerCase() : '';

            const coincideTexto = filtroTexto === '' || textoID.includes(filtroTexto) || textoNombre.includes(filtroTexto);

            //--- Filtros avanzados: buscan en la fila de detalles del empleado ---
            // (si un campo no está en los detalles, se busca también en la fila
            //  principal; ej. 'cargo' solo existe ahí en filas creadas por JS)
            let coincideAvanzados = true;
            if (Object.keys(filtrosAv).length > 0) {
                const filaDetallesF = filaPrincipal.nextElementSibling;
                const contDetalle = (filaDetallesF && filaDetallesF.classList.contains('fila-detalles'))
                    ? filaDetallesF : null;
                for (const columna in filtrosAv) {
                    const celda = (contDetalle && contDetalle.querySelector(`[data-column="${columna}"]`)) ||
                        filaPrincipal.querySelector(`[data-column="${columna}"]`);
                    const valorCelda = normalizarTexto(celda ? celda.textContent : '');
                    // Coincide solo si el texto de la celda (o alguno de sus
                    // valores separados por coma) es igual a un valor elegido
                    // (una celda vacía NO coincide con nada)
                    const ok = celdaCoincide(valorCelda, filtrosAv[columna]);
                    if (!ok) {
                        coincideAvanzados = false;
                        break;
                    }
                }
            }

            //--- Filtro por mes de nacimiento (formatos dd/mm/yyyy y yyyy-mm-dd) ---
            let coincideMes = true;
            if (filtroMesNac) {
                const filaDetallesM = filaPrincipal.nextElementSibling;
                const celdaFecha = filaDetallesM
                    ? filaDetallesM.querySelector('[data-column="fecha_nacimiento"]') : null;
                const fechaTxt = celdaFecha ? celdaFecha.textContent.trim() : '';
                // dd/mm/yyyy o dd-mm-yyyy → meses 01..12 en la posición 3-4
                // (sin anclar al final por si la celda trae también la hora)
                const m1 = fechaTxt.match(/^\d{2}[\/\-](\d{2})[\/\-]\d{4}/);
                // yyyy-mm-dd → mes en la posición 5-6
                const m2 = fechaTxt.match(/^\d{4}\-(\d{2})\-\d{2}/);
                const mesEmpleado = m1 ? m1[1] : (m2 ? m2[1] : '');
                coincideMes = mesEmpleado === filtroMesNac;
            }

            const filaDetalles = filaPrincipal.nextElementSibling;
            const hayFiltroActivo = filtroTexto !== '' ||
                Object.keys(filtrosAv).length > 0 || filtroMesNac !== '';

            if (coincideTexto && coincideAvanzados && coincideMes) {
                visibles++;
                filaPrincipal.style.display = '';
                if (filaDetalles && filaDetalles.classList.contains('fila-detalles') && hayFiltroActivo) {
                    filaDetalles.style.display = 'none';
                }
            } else {
                filaPrincipal.style.display = 'none';
                if (filaDetalles && filaDetalles.classList.contains('fila-detalles')) {
                    filaDetalles.style.display = 'none';
                }
            }
        });

        // Actualizar label con el total de empleados filtrados
        const totalLabel = document.getElementById('totalFiltradosLabel');
        if (totalLabel) {
            totalLabel.textContent = visibles + (visibles === 1 ? ' empleado' : ' empleados');
        }
    }

    //--- Panel: abrir/cerrar filtros avanzados ---
    window.toggleFiltrosAvanzados = function () {
        const panel = document.getElementById('panelFiltrosAvanzados');
        if (!panel) return;
        panel.classList.toggle('abierto');
        const btn = document.getElementById('btnToggleFiltrosAv');
        if (btn) btn.classList.toggle('panel-abierto', panel.classList.contains('abierto'));
    };

    //--- Limpia TODOS los filtros (búsqueda, contratos y avanzados) ---
    window.limpiarTodosLosFiltros = function () {
        const inputBusqueda = document.getElementById('inputBusquedaID');
        if (inputBusqueda) inputBusqueda.value = '';
        IDS_FILTROS_MULTIPLES.forEach(id => {
            const el = document.getElementById(id);
            if (el && typeof $ !== 'undefined') $(el).val(null).trigger('change');
        });
        const mesEl = document.getElementById(FILTRO_MES_NACIMIENTO);
        if (mesEl) mesEl.value = '';
        try {
            sessionStorage.removeItem('rrhh_filtro_busqueda');
            sessionStorage.removeItem('rrhh_filtro_avanzado');
        } catch (e) { /* almacenamiento no disponible */ }
        window.aplicarFiltrosEmpleados();
    };

    const inputBusqueda = document.getElementById('inputBusquedaID');

    // Restaurar filtros guardados (para no perder la búsqueda al recargar)
    try {
        const filtroBusquedaGuardado = sessionStorage.getItem('rrhh_filtro_busqueda');
        if (inputBusqueda && filtroBusquedaGuardado !== null) {
            inputBusqueda.value = filtroBusquedaGuardado;
        }
    } catch (e) { /* no se pudo restaurar el filtro */ }

    if (inputBusqueda) {
        inputBusqueda.addEventListener('input', window.aplicarFiltrosEmpleados);
    }

    //--- Filtros avanzados: restaurar valores guardados y conectar eventos ---
    try {
        const guardadoAv = JSON.parse(sessionStorage.getItem('rrhh_filtro_avanzado') || '{}');
        // Migración: tipos de contrato guardados con la clave antigua (cuando el
        // filtro estaba en la barra superior) se incorporan al panel avanzado
        if (!Array.isArray(guardadoAv.filtroTipoContrato)) {
            const legacy = JSON.parse(sessionStorage.getItem('rrhh_filtro_contratos') || '[]');
            if (Array.isArray(legacy) && legacy.length) guardadoAv.filtroTipoContrato = legacy;
        }
        sessionStorage.removeItem('rrhh_filtro_contratos');
        IDS_FILTROS_AV.forEach(id => {
            const el = document.getElementById(id);
            if (!el) return;
            if (id === FILTRO_MES_NACIMIENTO) {
                if (guardadoAv[id]) el.value = guardadoAv[id];
                el.addEventListener('change', window.aplicarFiltrosEmpleados);
            } else if (Array.isArray(guardadoAv[id]) && guardadoAv[id].length) {
                // Se aplica sobre el select nativo; Select2 lo refleja al inicializarse
                $(el).val(guardadoAv[id]);
            }
        });
    } catch (e) { /* no se pudo restaurar el filtro */ }

    IDS_FILTROS_MULTIPLES.forEach(id => {
        const el = document.getElementById(id);
        if (!el) return;
        // Mismo trato que el filtro de contratos: jQuery .on() + eventos Select2
        $(el).on('change select2:select select2:unselect select2:clear',
            window.aplicarFiltrosEmpleados);
    });

    //------------------------------------------------------
    //--- SELECT2 PARA LOS FILTROS AVANZADOS (multi) -------
    // (incluye el filtro de tipo de contrato, que vive en el panel)
    //------------------------------------------------------
    let _select2FiltroRetries = 0;
    const _SELECT2_FILTRO_MAX_RETRIES = 20;
    function initSelect2FiltrosAvanzados() {
        if (_select2FiltroRetries >= _SELECT2_FILTRO_MAX_RETRIES) {
            console.warn('Select2 (filtros avanzados) no disponible después de ' + _select2FiltroRetries + ' intentos');
            return;
        }
        _select2FiltroRetries++;
        if (typeof $ !== 'undefined' && $.fn && $.fn.select2) {
            IDS_FILTROS_MULTIPLES.forEach(id => {
                const el = document.getElementById(id);
                if (!el) return;
                const $el = $(el);
                if ($el.hasClass('select2-hidden-accessible')) return;
                $el.select2({
                    placeholder: el.dataset.placeholder || 'Todos',
                    allowClear: true,
                    closeOnSelect: false, // permite elegir varios sin cerrar el menú
                    width: '100%'
                });
            });
        } else {
            setTimeout(initSelect2FiltrosAvanzados, 500);
        }
    }
    initSelect2FiltrosAvanzados();

    // Mostrar el total inicial de empleados al cargar
    if (window.aplicarFiltrosEmpleados) window.aplicarFiltrosEmpleados();


    //------------------------------------------------------
    //------------- RESTABLECER CONTRASEÑA ---------------
    //------------------------------------------------------
    document.addEventListener('click', function (e) {
        const btnReset = e.target.closest('.btn-restablecer');
        if (btnReset) {
            e.preventDefault();
            const id = btnReset.dataset.id;
            if (!id) return;

            Swal.fire({
                title: '¿Restablecer contraseña?',
                text: 'La contraseña se cambiará por su número de identificación y se marcará como primer ingreso para que el usuario la cambie al iniciar sesión.',
                icon: 'question',
                showCancelButton: true,
                confirmButtonColor: '#2563eb',
                cancelButtonColor: '#6b7280',
                confirmButtonText: '<i class="fa-solid fa-check"></i> Sí, restablecer',
                cancelButtonText: 'Cancelar',
                showLoaderOnConfirm: true,
                preConfirm: async () => {
                    try {
                        // Incluir token CSRF si está disponible
                        const csrfInput = document.querySelector('input[name="csrf_token"]');
                        const headers = { 'Content-Type': 'application/json' };
                        if (csrfInput && csrfInput.value) {
                            headers['X-CSRFToken'] = csrfInput.value;
                        }
                        const resp = await fetch(`${getBaseUrl()}/rrhh/empleados/restablecer-password/${id}`, {
                            method: 'POST',
                            headers: headers,
                            body: JSON.stringify({})
                        });
                        const data = await resp.json();
                        if (!data.success) {
                            throw new Error(data.error || 'Error al restablecer contraseña');
                        }
                        return data;
                    } catch (err) {
                        Swal.showValidationMessage(err.message);
                    }
                }
            }).then((result) => {
                if (result.isConfirmed && result.value) {
                    Swal.fire({
                        title: '¡Contraseña restablecida!',
                        html: `<div style="text-align: left;">
                            <p>✅ La contraseña se ha restablecido exitosamente.</p>
                            <p style="margin-top: 10px;"><strong>Nueva contraseña temporal:</strong></p>
                            <div style="
                                background: #f0fdf4;
                                border: 2px dashed #22c55e;
                                border-radius: 10px;
                                padding: 12px 16px;
                                font-size: 1.2rem;
                                font-weight: 700;
                                text-align: center;
                                color: #166534;
                                letter-spacing: 2px;
                                margin-top: 6px;
                            ">${result.value.message.split(': ')[1] || 'Identificación del empleado'}</div>
                            <p style="margin-top: 12px; color: #64748b; font-size: 0.9rem;">
                                <i class="fa-solid fa-info-circle"></i> El usuario deberá cambiar la contraseña al iniciar sesión.
                            </p>
                        </div>`,
                        icon: 'success',
                        confirmButtonColor: '#2563eb',
                        confirmButtonText: 'Aceptar'
                    });
                }
            });
            return;
        }

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
    //------------------------------------------------------
    //--- SELECTOR DE ACCIÓN (TARJETAS) PARA EDIT CONTRATO --
    //------------------------------------------------------
    window.selectAccion = function(el) {
        // Remover selección de todas las opciones
        document.querySelectorAll('.accion-option').forEach(opt => opt.classList.remove('selected'));
        // Marcar la seleccionada
        el.classList.add('selected');
        const accion = el.dataset.accion;
        document.getElementById('accion').value = accion;

        // Ocultar todos los campos dinámicos
        document.querySelectorAll('.dynamic-field').forEach(f => f.style.display = 'none');

        // Mostrar según la acción
        const show = (...ids) => ids.forEach(id => {
            const el = document.getElementById(id);
            if (el) el.style.display = 'block';
        });

        const camposCargo = ['cargos', 'salarios', 'fechaInicio', 'descripcion'];
        const camposSalario = ['salarios', 'fechaInicio', 'descripcion'];
        const camposContrato = ['nuevoTipoContrato', 'salarios', 'fechaInicio', 'descripcion'];
        const camposProrroga = ['fechaInicio', 'fechaFin', 'descripcion'];
        const camposCrearContrato = ['nuevoTipoContrato', 'salarios', 'fechaInicio'];

        if (accion === 'crear_contrato') show(...camposCrearContrato);
        else if (accion === 'cambio_cargo') show(...camposCargo);
        else if (accion === 'cambio_salario') show(...camposSalario);
        else if (accion === 'cambio_contrato') show(...camposContrato);
        else if (accion === 'prorroga') show(...camposProrroga);
        else if (accion === 'editar_otrosi') show('fechaFin');
        // eliminar_contrato: no muestra campos dinámicos (todo oculto)

        // Para eliminar, disparar la confirmación al instante (no requiere Guardar).
        // requestSubmit dispara el evento submit; como formEditContrato no tiene campos
        // required, la validación HTML no bloquea la confirmación.
        if (accion === 'eliminar_contrato') {
            const formEdit = document.getElementById('formEditContrato');
            if (formEdit && typeof formEdit.requestSubmit === 'function') {
                formEdit.requestSubmit();
            } else if (formEdit) {
                formEdit.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
            }
        }
    };

    window.AbrirModalEditContrato = function (id) {
        fetch(`${getBaseUrl()}/rrhh/empleados/${id}/json`, {
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
            .then(res => res.json())
            .then(resp => {
                if (!resp.success) return Swal.fire('Error', 'Error al cargar datos', 'error');
                const emp = resp.empleado;
                
                // Detectar si el empleado tiene contrato (sin contrato => flujo de creación inicial)
                const tieneContrato = !!(emp.n_consecutivo);

                // Actualizar info bar
                document.getElementById('tituloContrato').textContent = tieneContrato
                    ? `Edición: ${emp.tipo_contrato} — Código ${emp.n_consecutivo}`
                    : 'Nuevo Contrato Inicial';
                document.getElementById('infoCodigo').textContent = emp.n_consecutivo || '—';
                document.getElementById('infoTipo').textContent = emp.tipo_contrato || '—';
                document.getElementById('infoOtrosi').textContent = emp.cuenta_otrosi || 0;
                document.getElementById('contratoInfoBar').style.display = 'flex';

                // Resetear valores del formulario ANTES de asignar los inputs ocultos:
                // form.reset() restaura TODOS los campos (incluidos los hidden) a su
                // valor HTML vacío, por lo que debe ejecutarse antes de setear los datos.
                document.getElementById('formEditContrato').reset();
                document.getElementById('salario_basico_edit').value = '';
                document.getElementById('factor_no_salarial_edit').value = '';

                document.getElementById('id_empleado_edit_contrato').value = emp.id;
                document.getElementById('consecutivo_edit_contrato').value = emp.n_consecutivo;
                document.getElementById('cuenta_otrosi').value = emp.cuenta_otrosi || 0;

                const idContrato = parseInt(emp.tipo_contrato_id);

                // Resetear selector de acciones
                document.querySelectorAll('.accion-option').forEach(opt => {
                    opt.classList.remove('selected');
                    opt.style.display = ''; // restaurar visibilidad
                });
                document.getElementById('accion').value = '';

                // Ocultar todos los campos dinámicos
                document.querySelectorAll('.dynamic-field').forEach(f => f.style.display = 'none');

                // Empleado SIN contrato: solo se permite crear el contrato inicial
                if (!tieneContrato) {
                    document.querySelectorAll('.accion-option').forEach(opt => {
                        if (opt.dataset.accion !== 'crear_contrato') {
                            opt.style.display = 'none';
                        }
                    });
                    document.getElementById('modalEditContrato').classList.add('active');
                    return;
                }

                // Empleado CON contrato: ocultar la creación inicial (evita contratos activos duplicados)
                document.querySelectorAll('.accion-option').forEach(opt => {
                    if (opt.dataset.accion === 'crear_contrato') {
                        opt.style.display = 'none';
                    }
                });

                // Lógica de visibilidad de opciones según tipo de contrato
                const prorrogaOpt = document.querySelector('.accion-option[data-accion="prorroga"]');
                const cargoOpt = document.querySelector('.accion-option[data-accion="cambio_cargo"]');
                const salarioOpt = document.querySelector('.accion-option[data-accion="cambio_salario"]');

                if (idContrato === 2 || idContrato === 5) {
                    // Contrato fijo o indefinido temporal: permitir prórroga
                    if (prorrogaOpt) prorrogaOpt.style.display = '';
                } else {
                    if (prorrogaOpt) prorrogaOpt.style.display = 'none';
                }

                if (idContrato === 5) {
                    // Indefinido temporal: ocultar cambio de cargo/salario
                    if (cargoOpt) cargoOpt.style.display = 'none';
                    if (salarioOpt) salarioOpt.style.display = 'none';
                }

                // "Editar Otrosí" solo se muestra si el último contrato tiene Otrosí
                const accionEditarOtrosi = document.getElementById('accionEditarOtrosi');
                if (accionEditarOtrosi) {
                    accionEditarOtrosi.style.display = (emp.cuenta_otrosi > 0) ? '' : 'none';
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
                codigoContrato: codigoContrato,
                tipo_contrato_id: document.getElementById('nuevo_tipo_contrato').value,
            };

            // Validación para creación de contrato inicial
            if (accion === 'crear_contrato') {
                const tipoNuevo = document.getElementById('nuevo_tipo_contrato').value;
                const fechaInicioNuevo = document.getElementById('fecha_inicio_prorroga').value;
                if (!tipoNuevo || !fechaInicioNuevo) {
                    return Swal.fire('Error', 'Debe seleccionar el tipo de contrato y la fecha de inicio', 'warning');
                }
            }

            // Validación para edición del último Otrosí: solo requiere la fecha de finalización
            if (accion === 'editar_otrosi') {
                const fechaFinOtrosi = document.getElementById('fecha_final_prorroga').value;
                if (!fechaFinOtrosi) {
                    return Swal.fire('Error', 'Debe ingresar la fecha de finalización del Otrosí', 'warning');
                }
            }

            const enviarSolicitud = () => {
                fetch(`${getBaseUrl()}/rrhh/otrosi/procesar_otrosi/${idEmpleado}`, {
                    method: 'POST',
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload)
                })
                    .then(res => res.json())
                    .then(resp => {
                        if(!resp.success) return Swal.fire('Error', 'Error: ' + resp.error, 'error');
                        if (accion === 'eliminar_contrato') {
                            Swal.fire('Éxito', 'Contrato eliminado correctamente', 'success');
                        } else if (accion === 'crear_contrato') {
                            Swal.fire('Éxito', 'Contrato creado correctamente', 'success');
                        } else {
                            Swal.fire('Éxito', `Proceso de "${accion.replace('_', ' ')}" realizado con exito`, 'success');
                        }
                        location.reload();
                    })
                    .catch(err => Swal.fire('Error', 'Error de comunicación con el servidor', 'error'));
            };

            if (accion === 'eliminar_contrato') {
                Swal.fire({
                    title: '¿Eliminar contrato?',
                    text: 'Esta acción eliminará el contrato y todos sus Otrosí. El empleado quedará sin contrato. No se puede deshacer.',
                    icon: 'warning',
                    showCancelButton: true,
                    confirmButtonColor: '#dc2626',
                    cancelButtonColor: '#64748b',
                    confirmButtonText: 'Sí, eliminar',
                    cancelButtonText: 'Cancelar'
                }).then(result => {
                    if (result.isConfirmed) enviarSolicitud();
                });
            } else {
                enviarSolicitud();
            }
        });
    }
    window.cerrarEditContrato = function () {
        const modal = document.getElementById('modalEditContrato');
        if (modal) {
            modal.classList.remove('active');
            document.getElementById('id_empleado_edit_contrato').value = "";
            document.getElementById('consecutivo_edit_contrato').value = "";
            document.getElementById('formEditContrato').reset();
            // Resetear campos ocultos
            ['cargos','salarios','fechaInicio','fechaFin','descripcion','nuevoTipoContrato'].forEach(id => {
                const el = document.getElementById(id);
                if (el) el.style.display = '';
            });
        }
    };

    //------------------------------------------------------
    //--- CAMBIO DE PESTAÑAS EN DETALLE DE EMPLEADOS -----
    //------------------------------------------------------
    window.switchDetalleTab = function(btn, tabName) {
        // Encuentra el contenedor de tabs más cercano
        const tabsContainer = btn.closest('.detalle-tabs');
        if (!tabsContainer) return;

        // Desactivar todos los botones y paneles
        tabsContainer.querySelectorAll('.detalle-tab-btn').forEach(b => b.classList.remove('active'));
        tabsContainer.querySelectorAll('.detalle-tab-panel').forEach(p => p.classList.remove('active'));

        // Activar el botón clickeado
        btn.classList.add('active');

        // Activar el panel correspondiente
        const panel = tabsContainer.querySelector(`.detalle-tab-panel[data-tab="${tabName}"]`);
        if (panel) panel.classList.add('active');
    };

    //------------------------------------------------------
    //----------- MODAL CONSECUTIVO DE CONTRATOS -----------
    //------------------------------------------------------
    function getModalConsecutivo() { return document.getElementById('modalConsecutivo'); }
    document.addEventListener('click', function (e) {
        const btnConsecutivo = e.target.closest('.btn-consecutivo')
        if (btnConsecutivo) {
            e.preventDefault();
            const idContrato = btnConsecutivo.dataset.id;
            console.log('btn-consecutivo click detected, id=', idContrato);
            AbrirModalEditConsecutivo(idContrato);
        }
    });
    window.AbrirModalEditConsecutivo = function (id) {
        console.log('AbrirModalEditConsecutivo called with id=', id);
        fetch(`${getBaseUrl()}/rrhh/contratos/${id}`)
            .then(res => res.json())
            .then(resp => {
                console.log('respuesta contrato:', resp);
                if (!resp.success) return Swal.fire('Error', 'Error al cargar datos', 'error');
                const contrato = resp.contratos;
                document.getElementById('tituloContrato_Consecutivo').textContent = `Editar el Consecutivo para los contratos tipo: ${contrato.nombre}`;
                document.getElementById('id_contrato_consecutivo').value = id;
                const consecutvo = document.getElementById('ult_consecutivo').value = contrato.ult_consecutivo;
                const modalConsecutivo = getModalConsecutivo();
                if (modalConsecutivo) {
                    modalConsecutivo.classList.add('active');
                } else {
                    console.warn('modalConsecutivo no encontrado en el DOM');
                }
            });
    };
    window.cerrarModalConsecutivo = function () {
        const modalConsecutivo = getModalConsecutivo();
        if (modalConsecutivo) modalConsecutivo.classList.remove('active');
    };
    const formConsecutivo = document.getElementById('formConsecutivo');
    if (formConsecutivo) {
        formConsecutivo.addEventListener('submit', function (e) {
            e.preventDefault()
            const id = document.getElementById('id_contrato_consecutivo').value;
            const valor = document.getElementById('ult_consecutivo').value;

            fetch(`${getBaseUrl()}/rrhh/contratos/consecutivo/editar/${id}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ ult_consecutivo: valor })
            })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        Swal.fire('Éxito', 'Consecutivo actualizado con exito', 'success');
                        cerrarModalConsecutivo();
                        location.reload();
                    } else {
                        Swal.fire('Error', 'error: ' + data.error, 'error');
                    }
                })
                .catch(err => {
                    console.error(err);
                    Swal.fire('Error', 'Error al conectar con el servidor', 'error');
                });
        });
    }
});

//------------------------------------------------------
//--------- IMPORTAR CONTRATOS MASIVOS ---------
//------------------------------------------------------
window.abrirModalImportarContratos = function () {
    document.getElementById('modalImportarContratos').classList.add('active');
    const resDiv = document.getElementById('resultadoImportarContratos');
    resDiv.className = 'import-result';
    resDiv.innerHTML = '';
};

window.cerrarModalImportarContratos = function () {
    const modal = document.getElementById('modalImportarContratos');
    if (!modal) return;
    if (modal.classList.contains('closing')) return;
    modal.classList.add('closing');
    setTimeout(() => {
        modal.classList.remove('active', 'closing');
        document.getElementById('formImportarContratos').reset();
        const resDiv = document.getElementById('resultadoImportarContratos');
        resDiv.className = 'import-result';
        resDiv.innerHTML = '';
    }, 200);
};

document.addEventListener('DOMContentLoaded', function () {
    const btnCargar = document.getElementById('btnCargarContratos');
    if (!btnCargar) return;
    btnCargar.addEventListener('click', function () {
        const fileInput = document.getElementById('archivo_contratos');
        const resDiv = document.getElementById('resultadoImportarContratos');
        const formData = new FormData();
        const csrfInput = document.querySelector('input[name="csrf_token"]');
        if (csrfInput && csrfInput.value) {
            formData.append('csrf_token', csrfInput.value);
        }
        if (!fileInput || fileInput.files.length === 0) {
            Swal.fire('Advertencia', 'Por favor, seleccione un archivo Excel.', 'warning');
            return;
        }
        formData.append('file', fileInput.files[0]);
        btnCargar.disabled = true;
        btnCargar.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Procesando...';
        resDiv.className = 'import-result show';
        resDiv.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Subiendo y procesando archivo...';
        resDiv.style.color = '#475569';
        fetch(`${getBaseUrl()}/rrhh/empleados/importar_contratos`, {
            method: 'POST',
            body: formData
        })
            .then(res => res.json().then(data => ({ status: res.status, data: data })))
            .then(({ status, data }) => {
                if (status === 200 && data.success) {
                    const procesados = data.procesados || 0;
                    const errores = data.errores_count || 0;
                    if (errores > 0) {
                        resDiv.className = 'import-result show import-warning';
                        let html = `<div class="import-result-summary">⚠️ Proceso completado con errores<br>`;
                        html += `<span class="count-ok">✅ ${procesados}</span> contratos procesados.<br>`;
                        html += `<span class="count-err">❌ ${errores}</span> contratos con errores.</div>`;
                        if (data.errores && data.errores.length > 0) {
                            html += `<div class="import-error-list">`;
                            data.errores.slice(0, 10).forEach(err => {
                                html += `<div class="import-error-item">
                                    <span class="import-error-fila">Fila ${err['FILA EXCEL']}</span>
                                    <span class="import-error-ident">${err['IDENTIFICACION']}</span>
                                    <span class="import-error-msg">${err['ERROR']}</span>
                                </div>`;
                            });
                            if (data.errores.length > 10) {
                                html += `<div class="import-error-more">... y ${data.errores.length - 10} errores más</div>`;
                            }
                            html += `</div>`;
                        }
                        if (data.error_excel_url) {
                            html += `<a href="${data.error_excel_url}" class="import-error-download" download>
                                <i class="fa-solid fa-file-excel"></i> Descargar Excel con errores
                            </a>`;
                        }
                        resDiv.innerHTML = html;
                    } else {
                        resDiv.className = 'import-result show import-success';
                        resDiv.innerHTML = `<div class="import-result-summary">✅ ¡Éxito! Se procesaron <strong>${procesados}</strong> contratos correctamente.</div>`;
                        setTimeout(() => { location.reload(); }, 2000);
                    }
                } else {
                    resDiv.className = 'import-result show import-error';
                    resDiv.innerHTML = `<div class="import-result-summary">❌ Error: ${data.error || 'Error desconocido'}</div>`;
                }
                btnCargar.disabled = false;
                btnCargar.innerHTML = '<i class="fa-solid fa-cloud-arrow-up"></i> Procesar Carga';
            })
            .catch(err => {
                console.error('Error importando contratos:', err);
                resDiv.className = 'import-result show import-error';
                resDiv.innerHTML = `<div class="import-result-summary">❌ Error de conexión: ${err.message}</div>`;
                btnCargar.disabled = false;
                btnCargar.innerHTML = '<i class="fa-solid fa-cloud-arrow-up"></i> Procesar Carga';
            });
    });
});

//------------------------------------------------------
//--------- ASIGNAR ROL SGI MASIVO ---------
//------------------------------------------------------
window.abrirModalAsignarRolSGI = function () {
    document.getElementById('modalAsignarRolSGI').classList.add('active');
    const resDiv = document.getElementById('resultadoAsignarRolSGI');
    resDiv.className = 'import-result';
    resDiv.innerHTML = '';
};

window.cerrarModalAsignarRolSGI = function () {
    const modal = document.getElementById('modalAsignarRolSGI');
    if (!modal) return;
    if (modal.classList.contains('closing')) return;
    modal.classList.add('closing');
    setTimeout(() => {
        modal.classList.remove('active', 'closing');
        document.getElementById('formAsignarRolSGI').reset();
        const resDiv = document.getElementById('resultadoAsignarRolSGI');
        resDiv.className = 'import-result';
        resDiv.innerHTML = '';
    }, 200);
};

document.addEventListener('DOMContentLoaded', function () {
    const btnCargar = document.getElementById('btnCargarRolSGI');
    if (!btnCargar) return;
    btnCargar.addEventListener('click', function () {
        const fileInput = document.getElementById('archivo_rol_sgi');
        const resDiv = document.getElementById('resultadoAsignarRolSGI');
        const formData = new FormData(document.getElementById('formAsignarRolSGI'));
        
        if (!fileInput || fileInput.files.length === 0) {
            Swal.fire('Advertencia', 'Por favor, seleccione un archivo Excel.', 'warning');
            return;
        }
        
        formData.append('file', fileInput.files[0]);
        
        btnCargar.disabled = true;
        btnCargar.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Procesando...';
        resDiv.className = 'import-result show';
        resDiv.innerHTML = '<div class="import-result-summary"><i class="fa-solid fa-spinner fa-spin"></i> Subiendo y procesando archivo...</div>';
        
        fetch(getBaseUrl() + '/rrhh/empleados/asignar_rol_sgi', {
            method: 'POST',
            body: formData
        })
        .then(res => res.json())
        .then(data => {
            btnCargar.disabled = false;
            btnCargar.innerHTML = '<i class="fa-solid fa-cloud-arrow-up"></i> Procesar Carga';
            
            if (data.success) {
                const procesados = data.procesados || 0;
                const erroresCount = data.errores_count || 0;
                
                if (erroresCount > 0) {
                    resDiv.className = 'import-result show import-warning';
                    let html = '<div class="import-result-summary">';
                    html += '<span class="count-ok">✅ ' + procesados + '</span> empleados actualizados.<br>';
                    html += '<span class="count-err">❌ ' + erroresCount + '</span> con errores.';
                    html += '</div>';
                    
                    if (data.errores && data.errores.length > 0) {
                        html += '<div class="import-error-list">';
                        data.errores.slice(0, 10).forEach(function(err) {
                            html += '<div class="import-error-item">';
                            html += '<span class="import-error-fila">Fila ' + (err['FILA EXCEL'] || '?') + '</span>';
                            html += '<span class="import-error-ident">' + (err['IDENTIFICACION'] || '') + '</span>';
                            html += '<span class="import-error-msg">' + (err['ERROR'] || '') + '</span>';
                            html += '</div>';
                        });
                        if (data.errores.length > 10) {
                            html += '<div class="import-error-more">... y ' + (data.errores.length - 10) + ' errores mas</div>';
                        }
                        html += '</div>';
                    }
                    
                    if (data.error_excel_url) {
                        html += '<a href="' + data.error_excel_url + '" class="import-error-download" download><i class="fa-solid fa-file-excel"></i> Descargar Excel con errores</a>';
                    }
                    resDiv.innerHTML = html;
                } else {
                    resDiv.className = 'import-result show import-success';
                    resDiv.innerHTML = '<div class="import-result-summary">✅ Exito! Se actualizaron <strong>' + procesados + '</strong> empleados correctamente.</div>';
                    setTimeout(function() { location.reload(); }, 2000);
                }
            } else {
                resDiv.className = 'import-result show import-error';
                resDiv.innerHTML = '<div class="import-result-summary">❌ Error: ' + (data.error || 'Error desconocido') + '</div>';
            }
        })
        .catch(function(err) {
            btnCargar.disabled = false;
            btnCargar.innerHTML = '<i class="fa-solid fa-cloud-arrow-up"></i> Procesar Carga';
            resDiv.className = 'import-result show import-error';
            resDiv.innerHTML = '<div class="import-result-summary">❌ Error de conexion: ' + err.message + '</div>';
        });
    });
});


//------------------------------------------------------
//--------- ASIGNAR ROL SGI MASIVO ---------
//------------------------------------------------------
window.abrirModalAsignarRolSGI = function () {
    document.getElementById('modalAsignarRolSGI').classList.add('active');
    const resDiv = document.getElementById('resultadoAsignarRolSGI');
    resDiv.className = 'import-result';
    resDiv.innerHTML = '';
};

window.cerrarModalAsignarRolSGI = function () {
    const modal = document.getElementById('modalAsignarRolSGI');
    if (!modal) return;
    if (modal.classList.contains('closing')) return;
    modal.classList.add('closing');
    setTimeout(() => {
        modal.classList.remove('active', 'closing');
        document.getElementById('formAsignarRolSGI').reset();
        const resDiv = document.getElementById('resultadoAsignarRolSGI');
        resDiv.className = 'import-result';
        resDiv.innerHTML = '';
    }, 200);
};

document.addEventListener('DOMContentLoaded', function () {
    const btnCargar = document.getElementById('btnCargarRolSGI');
    if (!btnCargar) return;
    btnCargar.addEventListener('click', function () {
        const fileInput = document.getElementById('archivo_rol_sgi');
        const resDiv = document.getElementById('resultadoAsignarRolSGI');
        const formData = new FormData(document.getElementById('formAsignarRolSGI'));
        
        if (!fileInput || fileInput.files.length === 0) {
            Swal.fire('Advertencia', 'Por favor, seleccione un archivo Excel.', 'warning');
            return;
        }
        
        formData.append('file', fileInput.files[0]);
        
        btnCargar.disabled = true;
        btnCargar.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Procesando...';
        resDiv.className = 'import-result show';
        resDiv.innerHTML = '<div class="import-result-summary"><i class="fa-solid fa-spinner fa-spin"></i> Subiendo y procesando archivo...</div>';
        
        fetch(getBaseUrl() + '/rrhh/empleados/asignar_rol_sgi', {
            method: 'POST',
            body: formData
        })
        .then(res => res.json())
        .then(data => {
            btnCargar.disabled = false;
            btnCargar.innerHTML = '<i class="fa-solid fa-cloud-arrow-up"></i> Procesar Carga';
            
            if (data.success) {
                const procesados = data.procesados || 0;
                const erroresCount = data.errores_count || 0;
                
                if (erroresCount > 0) {
                    resDiv.className = 'import-result show import-warning';
                    let html = '<div class="import-result-summary">';
                    html += '<span class="count-ok">✅ ' + procesados + '</span> empleados actualizados.<br>';
                    html += '<span class="count-err">❌ ' + erroresCount + '</span> con errores.';
                    html += '</div>';
                    
                    if (data.errores && data.errores.length > 0) {
                        html += '<div class="import-error-list">';
                        data.errores.slice(0, 10).forEach(function(err) {
                            html += '<div class="import-error-item">';
                            html += '<span class="import-error-fila">Fila ' + (err['FILA EXCEL'] || '?') + '</span>';
                            html += '<span class="import-error-ident">' + (err['IDENTIFICACION'] || '') + '</span>';
                            html += '<span class="import-error-msg">' + (err['ERROR'] || '') + '</span>';
                            html += '</div>';
                        });
                        if (data.errores.length > 10) {
                            html += '<div class="import-error-more">... y ' + (data.errores.length - 10) + ' errores mas</div>';
                        }
                        html += '</div>';
                    }
                    
                    if (data.error_excel_url) {
                        html += '<a href="' + data.error_excel_url + '" class="import-error-download" download><i class="fa-solid fa-file-excel"></i> Descargar Excel con errores</a>';
                    }
                    resDiv.innerHTML = html;
                } else {
                    resDiv.className = 'import-result show import-success';
                    resDiv.innerHTML = '<div class="import-result-summary">✅ Exito! Se actualizaron <strong>' + procesados + '</strong> empleados correctamente.</div>';
                    setTimeout(function() { location.reload(); }, 2000);
                }
            } else {
                resDiv.className = 'import-result show import-error';
                resDiv.innerHTML = '<div class="import-result-summary">❌ Error: ' + (data.error || 'Error desconocido') + '</div>';
            }
        })
        .catch(function(err) {
            btnCargar.disabled = false;
            btnCargar.innerHTML = '<i class="fa-solid fa-cloud-arrow-up"></i> Procesar Carga';
            resDiv.className = 'import-result show import-error';
            resDiv.innerHTML = '<div class="import-result-summary">❌ Error de conexion: ' + err.message + '</div>';
        });
    });
});
