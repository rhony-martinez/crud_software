/**
 * @typedef {{ detail?: string | Array<{loc?: Array<string | number>, msg?: string}> }} ErrorPayload
 * @typedef {{ id: number, nombre: string, especialidad: string, correo: string }} Medico
 * @typedef {{ nombre: string, especialidad: string, correo: string }} MedicoInput
 * @typedef {{
 *   id: number,
 *   medico_id: number,
 *   paciente: string,
 *   fecha_hora: string,
 *   motivo: string | null,
 *   medico: { id: number, nombre: string, especialidad: string }
 * }} Cita
 * @typedef {{ medico_id: number, paciente: string, fecha_hora: string, motivo: string | null }} CitaInput
 */

const API_URL = (import.meta.env.VITE_API_URL ?? 'http://localhost:8000').replace(/\/+$/, '');

/** @type {Record<string, string>} */
const nombresCampos = {
	nombre: 'Nombre',
	especialidad: 'Especialidad',
	correo: 'Correo',
	medico_id: 'Médico',
	paciente: 'Paciente',
	fecha_hora: 'Fecha y hora',
	motivo: 'Motivo'
};

/**
 * @param {unknown} payload
 * @param {number} status
 */
function mensajeDeError(payload, status) {
	const detail = /** @type {ErrorPayload | null} */ (payload)?.detail;

	if (typeof detail === 'string' && detail.trim()) {
		return detail;
	}

	if (Array.isArray(detail)) {
		const mensajes = detail
			.map((item) => {
				const campo = Array.isArray(item?.loc) ? item.loc.at(-1) : undefined;
				const nombreCampo = campo === undefined ? undefined : nombresCampos[String(campo)] ?? String(campo);
				const mensaje = item?.msg;
				return typeof mensaje === 'string'
					? nombreCampo
						? `${nombreCampo}: ${mensaje}`
						: mensaje
					: null;
			})
			.filter(Boolean);

		if (mensajes.length) {
			return mensajes.join('. ');
		}
	}

	return `La API respondió con el estado ${status}.`;
}

/**
 * @param {string} path
 * @param {RequestInit} [options]
 * @returns {Promise<unknown>}
 */
async function request(path, options = {}) {
	const headers = {
		Accept: 'application/json',
		...(options.body ? { 'Content-Type': 'application/json' } : {}),
		...options.headers
	};
	const response = await fetch(`${API_URL}${path}`, { ...options, headers });

	if (response.status === 204) {
		return null;
	}

	let payload;
	try {
		payload = await response.json();
	} catch {
		if (response.ok) {
			throw new Error('La API devolvió una respuesta que no es JSON válido.');
		}
		payload = null;
	}

	if (!response.ok) {
		throw new Error(mensajeDeError(payload, response.status));
	}

	return payload;
}

/** @param {unknown} error */
export function mensajeDeConexion(error) {
	if (error instanceof TypeError) {
		return 'No fue posible conectar con la API. Verifica que el backend esté activo.';
	}

	return error instanceof Error ? error.message : 'Ocurrió un error inesperado.';
}

/** @returns {Promise<{estado: string}>} */
export function obtenerEstadoApi() {
	return /** @type {Promise<{estado: string}>} */ (request('/salud'));
}

/** @returns {Promise<Medico[]>} */
export function listarMedicos() {
	return /** @type {Promise<Medico[]>} */ (request('/medicos'));
}

/** @param {MedicoInput} medico */
export function crearMedico(medico) {
	return request('/medicos', { method: 'POST', body: JSON.stringify(medico) });
}

/** @param {number} id @param {MedicoInput} medico */
export function actualizarMedico(id, medico) {
	return request(`/medicos/${id}`, { method: 'PUT', body: JSON.stringify(medico) });
}

/** @param {number} id */
export function eliminarMedico(id) {
	return request(`/medicos/${id}`, { method: 'DELETE' });
}

/** @returns {Promise<Cita[]>} */
export function listarCitas() {
	return /** @type {Promise<Cita[]>} */ (request('/citas'));
}

/** @param {CitaInput} cita */
export function crearCita(cita) {
	return request('/citas', { method: 'POST', body: JSON.stringify(cita) });
}

/** @param {number} id @param {CitaInput} cita */
export function actualizarCita(id, cita) {
	return request(`/citas/${id}`, { method: 'PUT', body: JSON.stringify(cita) });
}

/** @param {number} id */
export function eliminarCita(id) {
	return request(`/citas/${id}`, { method: 'DELETE' });
}
