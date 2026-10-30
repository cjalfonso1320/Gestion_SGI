from flask import Blueprint, render_template, request, jsonify, session, send_file, current_app
from flask_login import current_user, login_required
from controllers.matriz_controller import guardar_matriz, lista_matriz, modificar_matriz, lista_para_riesgos, obtener_activo_por_id, actualizar_activo_completo, importar_matriz_masiva_db
from controllers.rol_controller import PROCESOS_ROL, ROL_IMAGES, nombre_rol, list_roles

import pandas as pd
import io
from datetime import datetime

mActivos_bp = Blueprint('mActivos', __name__)


@mActivos_bp.route('/Matriz_Activos', defaults={'role_id': None})
@mActivos_bp.route('/Matriz_Activos/<int:role_id>')
@login_required
def Matriz_Activos(role_id):
    is_role_override = role_id is not None

    if is_role_override:
        session['selected_rol'] = role_id
        rol = role_id
    else:
        rol = session.get('selected_rol', current_user.rol)

    nombre_del_rol = nombre_rol(rol)
    lista_procesos = PROCESOS_ROL.get(rol, [])

    if not lista_procesos:
        return render_template('MatrizActivos/Matriz_Activos.html',
                               usuario=current_user,
                               lista_procesos=[],
                               proceso_actual=None,
                               datos_matriz=[],
                               rol_seleccionado=rol,
                               nombre_rol_seleccionado=nombre_del_rol,
                               is_role_override=is_role_override)

    proceso_solicitado = request.args.get('proceso')

    if proceso_solicitado in lista_procesos:
        proceso_actual = proceso_solicitado
    else:
        proceso_actual = lista_procesos[0]

    datos_matriz = lista_matriz(rol, proceso_actual)
    return render_template('MatrizActivos/Matriz_Activos.html',
                           usuario=current_user,
                           lista_procesos=lista_procesos,
                           proceso_actual=proceso_actual,
                           datos_matriz=datos_matriz,
                           rol_seleccionado=rol,
                           nombre_rol_seleccionado=nombre_del_rol,
                           is_role_override=is_role_override)

@mActivos_bp.route('/cargar_matriz_proceso')
@login_required
def cargar_matriz_proceso():
    rol_id = session.get('selected_rol', current_user.rol)
    proceso_solicitado = request.args.get('proceso')
    lista_procesos = PROCESOS_ROL.get(rol_id, [])

    # Validación de seguridad: Asegúrate de que el usuario tiene permiso para ver este proceso.
    if proceso_solicitado not in lista_procesos:
        return "<p>Error: Proceso no válido o no autorizado.</p>", 403

    # Carga los datos solo para el proceso solicitado
    datos_matriz = lista_matriz(rol_id, proceso_solicitado)

    # Renderiza SOLO la plantilla parcial y la devuelve como HTML
    return render_template('MatrizActivos/_matriz_template.html',
                           proceso=proceso_solicitado,
                           datos_matriz=datos_matriz)



@mActivos_bp.route('/guardarMatriz', methods=['POST'])
@login_required # Añadido por seguridad
def guardarMatriz():
    if request.method == 'POST':
        try:
            datos_form = {
                'tipoActivo': request.form.get('tipoActivo'),
                'nombre_activo': request.form.get('nombre_activo'),
                'cant_activo': request.form.get('cant_activo'),
                'responsable_activo': request.form.get('responsable_activo'),
                'clasificacionActivo': request.form.get('clasificacionActivo'),
                'ConfidencialidadActivo': request.form.get('ConfidencialidadActivo'),
                'IntegridadActivo': request.form.get('IntegridadActivo'),
                'DisponibilidadActivo': request.form.get('DisponibilidadActivo'),
                'TotalActivo': request.form.get('TotalActivo')
            }
            proceso = request.form.get('proceso')

            rol = current_user.rol
            nuevo_registro_tupla = guardar_matriz(rol, proceso, datos_form)
            
            # --- DICCIONARIO CORREGIDO ---
            # Las claves aquí deben coincidir con las que usa 'updateUiMatrizActivos' en JS
            nuevo_registro_dict = {
                "id": nuevo_registro_tupla[0],
                "tipoActivo": nuevo_registro_tupla[1],
                "nombre_activo": nuevo_registro_tupla[2], # Clave corregida
                "cant_activo": nuevo_registro_tupla[3],
                "responsable_activo": nuevo_registro_tupla[4],
                "clasificacionActivo": nuevo_registro_tupla[5],
                "ConfidencialidadActivo": nuevo_registro_tupla[6],
                "IntegridadActivo": nuevo_registro_tupla[7],
                "DisponibilidadActivo": nuevo_registro_tupla[8],
                "TotalActivo": nuevo_registro_tupla[9]
            }

            return jsonify({
                'success': True,
                'message': 'Matriz de Activos guardada Correctamente',
                'newData': nuevo_registro_dict
            })
        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({'success': False, 'message': f'Error al guardar: {str(e)}'})
    return jsonify({'success': False, 'message': 'Método no permitido'})
@mActivos_bp.route('/get_activo/<int:activo_id>')
@login_required
def get_activo(activo_id):
    try:
        activo = obtener_activo_por_id(activo_id)
        if not activo:
            return jsonify({'success': False, 'message': 'Activo no encontrado'}), 404
        return jsonify({'success': True, 'activo': activo})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@mActivos_bp.route('/actualizar_activo_completo', methods=['POST'])
@login_required
def actualizar_activo_completo_route():
    try:
        datos_form = {
            'tipoActivo': request.form.get('tipoActivo'),
            'nombre_activo': request.form.get('nombre_activo'),
            'cant_activo': request.form.get('cant_activo'),
            'responsable_activo': request.form.get('responsable_activo'),
            'clasificacionActivo': request.form.get('clasificacionActivo'),
            'ConfidencialidadActivo': request.form.get('ConfidencialidadActivo'),
            'IntegridadActivo': request.form.get('IntegridadActivo'),
            'DisponibilidadActivo': request.form.get('DisponibilidadActivo'),
            'TotalActivo': request.form.get('TotalActivo')
        }
        activo_id = request.form.get('edit_id')
        if not activo_id:
            return jsonify({'success': False, 'message': 'ID de activo no proporcionado'}), 400
        
        activo_actualizado = actualizar_activo_completo(activo_id, datos_form)
        if not activo_actualizado:
            return jsonify({'success': False, 'message': 'No se pudo actualizar el activo'}), 500
        
        return jsonify({
            'success': True,
            'message': 'Activo actualizado correctamente',
            'newData': activo_actualizado
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Error al actualizar: {str(e)}'}), 500


@mActivos_bp.route('/actualizar_activo', methods=['POST'])
@login_required
def actualizar_activo():
    try:
        data = request.get_json()
        activo_id = data.get('id')
        columna = data.get('columna')
        valor = data.get('valor')

        if not all([activo_id, columna, valor is not None]):
            return jsonify({
                'success': False,
                'message': 'Faltan Datos'
            }), 400
        nuevo_total = modificar_matriz(activo_id, columna, valor)
        return jsonify({
            'success': True,
            'message': 'Activo Actualizado Correctamente',
            'nuevo_total': nuevo_total
        })
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


#------------------------------------------------------
#--- DESCARGA PLANTILLA EXCEL PARA CARGA MASIVA -----
#------------------------------------------------------
@mActivos_bp.route('/descargar_plantilla_matriz')
@login_required
def descargar_plantilla_matriz():
    """Genera plantilla Excel para carga masiva de Matriz de Activos.
    Incluye las columnas 'rol_id' y 'proceso' que no se muestran en la tabla.
    """
    columnas = [
        'TIPO_ACTIVO',
        'NOMBRE',
        'CANTIDAD',
        'RESPONSABLE',
        'CLASIFICACION',
        'CONFIDENCIALIDAD',
        'INTEGRIDAD',
        'DISPONIBILIDAD',
        'TOTAL',
        'ROL_ID',
        'PROCESO',
    ]
    df = pd.DataFrame(columns=columnas)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Plantilla Matriz Activos')
        workbook = writer.book
        worksheet = writer.sheets['Plantilla Matriz Activos']

        # ── Hoja oculta con listas desplegables ──
        hidden_sheet = workbook.add_worksheet('ListasDesplegables')
        hidden_sheet.hide()

        # Lista de todos los roles de la BD: col A = nombre, col B = ID
        roles_bd = list_roles()  # [(id, nombre), ...]
        # Escribir los nombres de los roles en columna A
        for idx, (rid, rnombre) in enumerate(roles_bd):
            hidden_sheet.write(idx, 0, str(rnombre).upper())
            hidden_sheet.write(idx, 1, rid)
        hidden_sheet.set_column(0, 0, 30)
        hidden_sheet.set_column(1, 1, 8)

        # Validación: columna ROL_ID (col 9) con lista desplegable de nombres de roles
        worksheet.data_validation(1, 9, 10000, 9, {
            'validate': 'list',
            'source': f'=ListasDesplegables!$A$1:$A${len(roles_bd)}'
        })

        # Formato del encabezado
        header_fmt = workbook.add_format({
            'bold': True,
            'bg_color': '#1e3a8a',
            'font_color': '#ffffff',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True
        })
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_fmt)
            worksheet.set_column(col_num, col_num, 22)

        # Resaltar columnas adicionales (ROL_ID y PROCESO)
        highlight_fmt = workbook.add_format({
            'bg_color': '#fef3c7',
            'border': 1,
            'align': 'center',
            'font_color': '#92400e',
            'italic': True
        })
        # ROL_ID está en columna 9, PROCESO en columna 10
        txt = 'Selecciona el nombre del rol de la lista desplegable'
        worksheet.write(1, 9, txt, highlight_fmt)
        worksheet.write(1, 10, 'Nombre del proceso (ej: Complementacion)', highlight_fmt)
        worksheet.set_column(9, 9, 32)
        worksheet.set_column(10, 10, 30)

    output.seek(0)
    return send_file(
        output,
        download_name=f'plantilla_matriz_activos_{datetime.now().strftime("%Y%m%d")}.xlsx',
        as_attachment=True,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )


#------------------------------------------------------
#--- CARGA MASIVA DE MATRIZ DE ACTIVOS --------------
#------------------------------------------------------
@mActivos_bp.route('/cargar_matriz_masiva', methods=['POST'])
@login_required
def cargar_matriz_masiva():
    """Procesa un archivo Excel para carga masiva de activos.
    Inserta o actualiza registros en la tabla matriz_activo.
    """
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No se ha proporcionado ningún archivo.'}), 400

    file = request.files['file']
    rol_id = request.form.get('rol_id', type=int)
    proceso_defecto = request.form.get('proceso', '')

    if not rol_id:
        rol_id = session.get('selected_rol', current_user.rol)

    try:
        df = pd.read_excel(file)
        df.columns = [str(c).strip().upper() for c in df.columns]

        # Mapeo de nombres de columnas esperados
        columnas_esperadas = {
            'TIPO_ACTIVO': 'tipo_activo',
            'NOMBRE': 'nombre',
            'CANTIDAD': 'cantidad',
            'RESPONSABLE': 'responsable',
            'CLASIFICACION': 'clasificacion',
            'CONFIDENCIALIDAD': 'confidencialidad',
            'INTEGRIDAD': 'integridad',
            'DISPONIBILIDAD': 'disponibilidad',
            'TOTAL': 'total',
            'ROL_ID': 'id_rol',
            'PROCESO': 'proceso',
        }

        # Mapa de nombre de rol → ID (para cuando el usuario use la lista desplegable con nombres)
        roles_bd = list_roles()  # [(id, nombre), ...]
        roles_map = {str(r[1]).strip().upper(): r[0] for r in roles_bd}

        insertados = 0
        errores = []

        for idx, (_, row) in enumerate(df.iterrows()):
            r = row.to_dict()
            numero_fila = idx + 2  # +2 porque fila 1 es encabezado

            try:
                data = {}
                for col_excel, col_db in columnas_esperadas.items():
                    val = r.get(col_excel)
                    if pd.isna(val) or str(val).strip().lower() == 'nan':
                        val = None
                    data[col_db] = val

                # Si no se especifica rol_id o proceso, usar los valores por defecto
                if data.get('id_rol') is None or str(data.get('id_rol', '')).strip() == '':
                    data['id_rol'] = rol_id
                else:
                    rol_val = str(data['id_rol']).strip()
                    # Intentar convertir a entero (ID numérico)
                    try:
                        data['id_rol'] = int(float(rol_val))
                    except (ValueError, TypeError):
                        # Si no es numérico, buscar por nombre de rol (desde la lista desplegable)
                        rol_upper = rol_val.upper()
                        if rol_upper in roles_map:
                            data['id_rol'] = roles_map[rol_upper]
                        else:
                            # Buscar coincidencia parcial: "BANCOLOMBIA" → encontrar el ID
                            encontrado = None
                            for rname, rid in roles_map.items():
                                if rol_upper in rname or rname in rol_upper:
                                    encontrado = rid
                                    break
                            data['id_rol'] = encontrado if encontrado is not None else rol_id

                if data.get('proceso') is None or str(data.get('proceso', '')).strip() == '':
                    data['proceso'] = proceso_defecto
                else:
                    data['proceso'] = str(data['proceso']).strip()

                # Calcular total si no se proporcionó
                if data.get('total') is None or str(data.get('total', '')).strip() == '':
                    c = int(data.get('confidencialidad') or 0)
                    i = int(data.get('integridad') or 0)
                    d = int(data.get('disponibilidad') or 0)
                    data['total'] = c + i + d
                else:
                    try:
                        data['total'] = int(float(str(data['total'])))
                    except (ValueError, TypeError):
                        data['total'] = 0

                exito, error = importar_matriz_masiva_db(data)
                if exito:
                    insertados += 1
                else:
                    errores.append({
                        'FILA EXCEL': numero_fila,
                        'NOMBRE': data.get('nombre', ''),
                        'ERROR': error
                    })
            except Exception as row_error:
                errores.append({
                    'FILA EXCEL': numero_fila,
                    'NOMBRE': r.get('NOMBRE', ''),
                    'ERROR': str(row_error)
                })
                continue

        response_data = {
            'success': True,
            'insertados': insertados,
            'total_filas': len(df),
            'errores_count': len(errores),
            'errores': errores
        }
        return jsonify(response_data)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': f'Error al procesar el archivo: {str(e)}'}), 400