<script>
	import { onMount } from 'svelte';
	import {
		actualizarCita,
		crearCita,
		eliminarCita,
		listarCitas,
		listarMedicos,
		mensajeDeConexion
	} from '#lib/api.js';

	/** @typedef {import('#lib/api.js').Cita} Cita */
	/** @typedef {import('#lib/api.js').Medico} Medico */
	/** @typedef {{id?: number, medico_id: string, paciente: string, fecha_hora: string, motivo: string}} CitaFormulario */

	const formularioVacio = () => ({
		medico_id: '',
		paciente: '',
		fecha_hora: '',
		motivo: ''
	});

	let citas = $state(/** @type {Cita[]} */ ([]));
	let medicos = $state(/** @type {Medico[]} */ ([]));
	let formulario = $state(/** @type {CitaFormulario} */ (formularioVacio()));
	let formularioAbierto = $state(false);
	let cargandoCitas = $state(true);
	let cargandoMedicos = $state(true);
	let guardando = $state(false);
	let eliminandoId = $state(/** @type {number | null} */ (null));
	let errorCitas = $state('');
	let errorMedicos = $state('');
	let errorAccion = $state('');
	let exito = $state('');

	const editando = $derived(formulario.id !== undefined);

	async function cargarCitas() {
		cargandoCitas = true;
		errorCitas = '';
		try {
			const resultado = await listarCitas();
			if (!Array.isArray(resultado)) {
				throw new Error('La API no devolvió una lista de citas válida.');
			}
			citas = resultado;
		} catch (error) {
			errorCitas = mensajeDeConexion(error);
		} finally {
			cargandoCitas = false;
		}
	}

	async function cargarMedicos() {
		cargandoMedicos = true;
		errorMedicos = '';
		try {
			const resultado = await listarMedicos();
			if (!Array.isArray(resultado)) {
				throw new Error('La API no devolvió una lista de médicos válida.');
			}
			medicos = resultado;
		} catch (error) {
			errorMedicos = mensajeDeConexion(error);
		} finally {
			cargandoMedicos = false;
		}
	}

	function abrirNuevo() {
		formulario = formularioVacio();
		formularioAbierto = true;
		errorAccion = '';
		exito = '';
	}

	/** @param {Cita} cita */
	function abrirEdicion(cita) {
		formulario = {
			id: cita.id,
			medico_id: String(cita.medico_id),
			paciente: cita.paciente,
			fecha_hora: String(cita.fecha_hora).slice(0, 16),
			motivo: cita.motivo ?? ''
		};
		formularioAbierto = true;
		errorAccion = '';
		exito = '';
	}

	function cancelarEdicion() {
		formularioAbierto = false;
		formulario = formularioVacio();
		errorAccion = '';
	}

	/** @param {string} valor */
	function fechaParaApi(valor) {
		return valor.length === 16 ? `${valor}:00` : valor;
	}

	/** @param {SubmitEvent} event */
	async function guardarCita(event) {
		event.preventDefault();
		guardando = true;
		errorAccion = '';
		exito = '';
		const datos = {
			medico_id: Number(formulario.medico_id),
			paciente: formulario.paciente.trim(),
			fecha_hora: fechaParaApi(formulario.fecha_hora),
			motivo: formulario.motivo.trim() || null
		};

		try {
			if (formulario.id !== undefined) {
				await actualizarCita(formulario.id, datos);
				exito = 'La cita se actualizó correctamente.';
			} else {
				await crearCita(datos);
				exito = 'La cita se registró correctamente.';
			}
			formularioAbierto = false;
			formulario = formularioVacio();
			await cargarCitas();
		} catch (error) {
			errorAccion = mensajeDeConexion(error);
		} finally {
			guardando = false;
		}
	}

	/** @param {Cita} cita */
	async function borrarCita(cita) {
		if (!confirm(`¿Deseas eliminar la cita de ${cita.paciente}?`)) {
			return;
		}

		eliminandoId = cita.id;
		errorAccion = '';
		exito = '';
		try {
			await eliminarCita(cita.id);
			exito = 'La cita se eliminó correctamente.';
			await cargarCitas();
		} catch (error) {
			errorAccion = mensajeDeConexion(error);
		} finally {
			eliminandoId = null;
		}
	}

	/** @param {string} fecha */
	function mostrarFecha(fecha) {
		const partes = /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})(?::(\d{2}))?/.exec(fecha);
		if (!partes) {
			return fecha;
		}
		const [, anio, mes, dia, hora, minuto, segundo = '0'] = partes;
		const fechaLocal = new Date(
			Number(anio),
			Number(mes) - 1,
			Number(dia),
			Number(hora),
			Number(minuto),
			Number(segundo)
		);
		return fechaLocal.toLocaleString('es-CO', {
			dateStyle: 'medium',
			timeStyle: 'short'
		});
	}

	onMount(() => {
		void cargarCitas();
		void cargarMedicos();
	});
</script>

<svelte:head>
	<title>Citas | Clínica</title>
	<meta name="description" content="Programa, consulta y administra las citas de los pacientes." />
</svelte:head>

<section class="page">
	<header class="page-heading">
		<div>
			<p class="eyebrow">AGENDA</p>
			<h1>Citas</h1>
			<p class="description">Programa las consultas y asigna cada paciente a un médico.</p>
		</div>
		<button class="button button-primary" type="button" onclick={abrirNuevo} disabled={cargandoMedicos || medicos.length === 0}>
			<span class="plus" aria-hidden="true">+</span> Nueva cita
		</button>
	</header>

	{#if errorAccion}
		<div class="alert alert-error" role="alert">
			<span class="alert-icon" aria-hidden="true">!</span>
			<p>{errorAccion}</p>
			<button class="alert-close" type="button" aria-label="Cerrar mensaje" onclick={() => (errorAccion = '')}>×</button>
		</div>
	{/if}
	{#if exito}
		<div class="alert alert-success" role="status">
			<span class="alert-icon" aria-hidden="true">✓</span>
			<p>{exito}</p>
			<button class="alert-close" type="button" aria-label="Cerrar mensaje" onclick={() => (exito = '')}>×</button>
		</div>
	{/if}
	{#if errorMedicos}
		<div class="alert alert-error" role="alert">
			<span class="alert-icon" aria-hidden="true">!</span>
			<p>No se pudo cargar la lista de médicos: {errorMedicos}</p>
			<button class="button button-secondary" type="button" onclick={cargarMedicos} disabled={cargandoMedicos}>Reintentar</button>
		</div>
	{:else if !cargandoMedicos && medicos.length === 0}
		<div class="alert alert-info" role="status">
			<span class="alert-icon" aria-hidden="true">i</span>
			<p>Registra al menos un médico antes de crear una cita.</p>
			<a href="/medicos">Ir a médicos <span aria-hidden="true">→</span></a>
		</div>
	{/if}

	{#if formularioAbierto}
		<section class="form-card panel" aria-labelledby="form-title">
			<div class="form-heading">
				<div>
					<p class="eyebrow">{editando ? 'ACTUALIZACIÓN' : 'NUEVO REGISTRO'}</p>
					<h2 id="form-title">{editando ? 'Editar cita' : 'Programar cita'}</h2>
				</div>
				<button class="icon-button" type="button" aria-label="Cerrar formulario" onclick={cancelarEdicion}>×</button>
			</div>

			<form onsubmit={guardarCita}>
				<div class="field-grid">
					<label class="field">
						<span>Médico <span class="required">*</span></span>
						<select bind:value={formulario.medico_id} class="input" name="medico_id" required>
							<option value="" disabled>Selecciona un médico</option>
							{#each medicos as medico (medico.id)}
								<option value={String(medico.id)}>{medico.nombre} · {medico.especialidad}</option>
							{/each}
						</select>
					</label>
					<label class="field">
						<span>Nombre del paciente <span class="required">*</span></span>
						<input
							bind:value={formulario.paciente}
							class="input"
							name="paciente"
							type="text"
							placeholder="Ej. Camila Torres"
							minlength="2"
							maxlength="100"
							autocomplete="name"
							required
						/>
					</label>
					<label class="field">
						<span>Fecha y hora <span class="required">*</span></span>
						<input
							bind:value={formulario.fecha_hora}
							class="input"
							name="fecha_hora"
							type="datetime-local"
							step="60"
							required
						/>
					</label>
					<label class="field">
						<span>Motivo de consulta</span>
						<input
							bind:value={formulario.motivo}
							class="input"
							name="motivo"
							type="text"
							placeholder="Ej. Control general"
							maxlength="200"
						/>
					</label>
				</div>
				<p class="form-hint"><span class="required">*</span> Campos obligatorios · La fecha se envía en formato local ISO 8601.</p>
				<div class="form-actions">
					<button class="button button-secondary" type="button" onclick={cancelarEdicion}>Cancelar</button>
					<button class="button button-primary" type="submit" disabled={guardando || medicos.length === 0}>
						{guardando ? 'Guardando…' : editando ? 'Guardar cambios' : 'Programar cita'}
					</button>
				</div>
			</form>
		</section>
	{/if}

	<section class="list-card panel" aria-labelledby="list-title">
		<div class="list-heading">
			<div>
				<h2 id="list-title">Agenda de citas</h2>
				<p>Consultas registradas en el sistema</p>
			</div>
			<div class="list-tools">
				<span class="record-count">{citas.length} {citas.length === 1 ? 'cita' : 'citas'}</span>
				<button class="refresh-button" type="button" onclick={cargarCitas} disabled={cargandoCitas}>
					<span aria-hidden="true">↻</span> Actualizar
				</button>
			</div>
		</div>

		{#if errorCitas}
			<div class="load-error" role="alert">
				<strong>No se pudo cargar la agenda.</strong>
				<span>{errorCitas}</span>
				<button class="button button-secondary" type="button" onclick={cargarCitas}>Reintentar</button>
			</div>
		{:else if cargandoCitas}
			<div class="loading-state" role="status">
				<span class="spinner" aria-hidden="true"></span> Cargando citas…
			</div>
		{:else if citas.length === 0}
			<div class="empty-state">
				<span class="empty-icon" aria-hidden="true">▦</span>
				<strong>Aún no hay citas registradas</strong>
				<p>Cuando programes una consulta, aparecerá aquí con el médico asignado.</p>
				<button class="button button-primary" type="button" onclick={abrirNuevo} disabled={medicos.length === 0}>
					Programar cita
				</button>
			</div>
		{:else}
			<div class="table-scroll">
				<table>
					<thead>
						<tr>
							<th scope="col">PACIENTE</th>
							<th scope="col">MÉDICO</th>
							<th scope="col">FECHA Y HORA</th>
							<th scope="col">MOTIVO</th>
							<th scope="col" class="actions-heading">ACCIONES</th>
						</tr>
					</thead>
					<tbody>
						{#each citas as cita (cita.id)}
							<tr>
								<td data-label="Paciente">
									<div class="patient-cell">
										<span class="patient-avatar" aria-hidden="true">{cita.paciente?.trim()?.charAt(0)?.toUpperCase() ?? 'P'}</span>
										<span>
											<strong>{cita.paciente}</strong>
											<small>ID #{cita.id}</small>
										</span>
									</div>
								</td>
								<td data-label="Médico">
									<span class="doctor-name">{cita.medico?.nombre ?? `Médico #${cita.medico_id}`}</span>
									{#if cita.medico?.especialidad}
										<small class="doctor-specialty">{cita.medico.especialidad}</small>
									{/if}
								</td>
								<td data-label="Fecha y hora">
									<span class="date-cell">{mostrarFecha(cita.fecha_hora)}</span>
								</td>
								<td data-label="Motivo"><span class="reason">{cita.motivo || 'Sin motivo especificado'}</span></td>
								<td data-label="Acciones">
									<div class="row-actions">
										<button class="action-button" type="button" onclick={() => abrirEdicion(cita)}>Editar</button>
										<button
											class="action-button delete-action"
											type="button"
											onclick={() => borrarCita(cita)}
											disabled={eliminandoId === cita.id}
										>
											{eliminandoId === cita.id ? 'Eliminando…' : 'Eliminar'}
										</button>
									</div>
								</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		{/if}
	</section>
</section>

<style>
	.page {
		max-width: 1120px;
		margin: 0 auto;
	}

	.page-heading {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 20px;
		margin-bottom: 24px;
	}

	.eyebrow {
		margin: 0 0 7px;
		color: #4e9b87;
		font-size: 10px;
		font-weight: 750;
		letter-spacing: 1.1px;
	}

	h1 {
		margin: 0;
		color: #1e2e45;
		font-size: 29px;
		font-weight: 700;
		letter-spacing: -0.8px;
	}

	.description {
		margin: 8px 0 0;
		color: #7c899a;
		font-size: 12px;
	}

	.button {
		display: inline-flex;
		min-height: 39px;
		align-items: center;
		justify-content: center;
		gap: 8px;
		padding: 0 15px;
		border: 1px solid transparent;
		border-radius: 7px;
		cursor: pointer;
		font-size: 11px;
		font-weight: 650;
		transition: background 140ms ease, transform 140ms ease;
	}

	.button:hover:not(:disabled) {
		transform: translateY(-1px);
	}

	.button:disabled {
		cursor: wait;
		opacity: 0.65;
	}

	.button-primary {
		background: #258d79;
		color: white;
	}

	.button-primary:hover:not(:disabled) {
		background: #1d7867;
	}

	.button-secondary {
		border-color: #dce4ed;
		background: white;
		color: #53647b;
	}

	.button-secondary:hover:not(:disabled) {
		background: #f7fafc;
	}

	.plus {
		font-size: 18px;
		font-weight: 400;
		line-height: 1;
	}

	.panel {
		border: 1px solid #e7edf3;
		border-radius: 11px;
		background: white;
		box-shadow: 0 3px 12px rgb(30 52 80 / 3%);
	}

	.alert {
		display: flex;
		align-items: center;
		gap: 10px;
		margin-bottom: 13px;
		padding: 11px 13px;
		border: 1px solid;
		border-radius: 8px;
	}

	.alert p {
		flex: 1;
		margin: 0;
		font-size: 11px;
		line-height: 1.5;
	}

	.alert-error {
		border-color: #f2d2d0;
		background: #fff7f6;
		color: #9f4845;
	}

	.alert-success {
		border-color: #c9e9df;
		background: #f3fbf8;
		color: #347b69;
	}

	.alert-info {
		border-color: #d7e6f3;
		background: #f5f9fd;
		color: #526d87;
	}

	.alert-icon {
		font-size: 13px;
		font-weight: 800;
	}

	.alert-close,
	.icon-button {
		border: 0;
		background: transparent;
		color: #8895a5;
		cursor: pointer;
		font-size: 19px;
		line-height: 1;
	}

	.alert a {
		margin-left: auto;
		color: #347b69;
		font-size: 10px;
		font-weight: 650;
		text-decoration: none;
		white-space: nowrap;
	}

	.alert a:hover {
		text-decoration: underline;
	}

	.form-card {
		margin-bottom: 17px;
		padding: 21px 23px 20px;
	}

	.form-heading {
		display: flex;
		align-items: flex-start;
		justify-content: space-between;
		margin-bottom: 20px;
	}

	.form-heading .eyebrow {
		margin-bottom: 5px;
	}

	.form-heading h2,
	.list-heading h2 {
		margin: 0;
		color: #26364c;
		font-size: 15px;
		font-weight: 680;
	}

	.field-grid {
		display: grid;
		grid-template-columns: repeat(2, minmax(0, 1fr));
		gap: 16px;
	}

	.field {
		display: grid;
		gap: 7px;
		color: #4e5c70;
		font-size: 11px;
		font-weight: 650;
	}

	.required {
		color: #d56360;
	}

	.input {
		width: 100%;
		min-height: 40px;
		padding: 0 11px;
		border: 1px solid #dce4ed;
		border-radius: 6px;
		background: #fff;
		color: #26364c;
		font-size: 12px;
		font-weight: 400;
	}

	.input::placeholder {
		color: #aab4c1;
	}

	.input:focus {
		border-color: #68b7a4;
		outline: 3px solid rgb(104 183 164 / 13%);
	}

	.form-hint {
		margin: 13px 0 0;
		color: #8793a2;
		font-size: 10px;
	}

	.form-actions {
		display: flex;
		justify-content: flex-end;
		gap: 9px;
		margin-top: 20px;
		padding-top: 15px;
		border-top: 1px solid #edf0f4;
	}

	.list-card {
		overflow: hidden;
	}

	.list-heading {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 15px;
		padding: 20px 22px;
	}

	.list-heading h2 {
		font-size: 14px;
	}

	.list-heading p {
		margin: 5px 0 0;
		color: #8b96a5;
		font-size: 10px;
	}

	.list-tools {
		display: flex;
		align-items: center;
		gap: 14px;
	}

	.record-count {
		padding: 5px 9px;
		border-radius: 20px;
		background: #edf7f4;
		color: #388976;
		font-size: 10px;
		font-weight: 650;
		white-space: nowrap;
	}

	.refresh-button {
		border: 0;
		background: transparent;
		color: #718096;
		cursor: pointer;
		font-size: 10px;
	}

	.refresh-button:disabled {
		cursor: wait;
		opacity: 0.5;
	}

	.refresh-button span {
		padding-right: 3px;
		font-size: 14px;
	}

	.table-scroll {
		overflow-x: auto;
		border-top: 1px solid #edf0f4;
	}

	table {
		width: 100%;
		border-collapse: collapse;
		text-align: left;
	}

	th {
		height: 39px;
		padding: 0 15px;
		background: #fafbfd;
		color: #8995a5;
		font-size: 9px;
		font-weight: 700;
		letter-spacing: 0.55px;
		white-space: nowrap;
	}

	td {
		padding: 13px 15px;
		border-top: 1px solid #f0f2f5;
		color: #57657a;
		font-size: 11px;
	}

	tbody tr:hover {
		background: #fcfdfd;
	}

	.actions-heading {
		text-align: right;
	}

	.patient-cell {
		display: flex;
		align-items: center;
		gap: 9px;
	}

	.patient-avatar {
		display: grid;
		width: 31px;
		height: 31px;
		flex: 0 0 auto;
		place-items: center;
		border-radius: 50%;
		background: #edf0fb;
		color: #6471b2;
		font-size: 11px;
		font-weight: 700;
	}

	.patient-cell strong,
	.patient-cell small {
		display: block;
	}

	.patient-cell strong {
		color: #2c3a50;
		font-size: 11px;
		font-weight: 650;
	}

	.patient-cell small {
		margin-top: 4px;
		color: #9aa4b1;
		font-size: 9px;
	}

	.doctor-name,
	.doctor-specialty {
		display: block;
	}

	.doctor-name {
		color: #46586f;
		font-weight: 600;
	}

	.doctor-specialty {
		margin-top: 4px;
		color: #95a0ae;
		font-size: 9px;
	}

	.date-cell {
		color: #41546d;
		white-space: nowrap;
	}

	.reason {
		color: #788698;
	}

	.row-actions {
		display: flex;
		justify-content: flex-end;
		gap: 5px;
	}

	.action-button {
		padding: 6px 7px;
		border: 1px solid #e1e7ee;
		border-radius: 5px;
		background: #fff;
		color: #52647a;
		cursor: pointer;
		font-size: 9px;
		white-space: nowrap;
	}

	.action-button:hover:not(:disabled) {
		border-color: #b7c8d7;
		background: #f8fafc;
	}

	.delete-action {
		border-color: #f0dddd;
		color: #b45b58;
	}

	.delete-action:hover:not(:disabled) {
		border-color: #e9bfbd;
		background: #fff7f6;
	}

	.action-button:disabled {
		cursor: wait;
		opacity: 0.6;
	}

	.loading-state,
	.empty-state,
	.load-error {
		display: flex;
		align-items: center;
		justify-content: center;
		border-top: 1px solid #edf0f4;
		color: #7e8b9c;
		font-size: 11px;
	}

	.loading-state {
		min-height: 150px;
		gap: 10px;
	}

	.spinner {
		width: 16px;
		height: 16px;
		border: 2px solid #dbe9e5;
		border-top-color: #409982;
		border-radius: 50%;
		animation: spin 700ms linear infinite;
	}

	@keyframes spin {
		to {
			transform: rotate(360deg);
		}
	}

	.empty-state {
		min-height: 240px;
		flex-direction: column;
		padding: 27px 20px;
		text-align: center;
	}

	.empty-icon {
		display: grid;
		width: 43px;
		height: 43px;
		place-items: center;
		margin-bottom: 10px;
		border-radius: 13px;
		background: #edf2fb;
		color: #6675b7;
		font-size: 20px;
	}

	.empty-state strong {
		color: #39495e;
		font-size: 12px;
	}

	.empty-state p {
		margin: 7px 0 15px;
		color: #8a96a5;
		font-size: 10px;
	}

	.load-error {
		min-height: 170px;
		flex-direction: column;
		gap: 8px;
		padding: 23px;
		text-align: center;
	}

	.load-error strong {
		color: #a24f4b;
		font-size: 12px;
	}

	.load-error span {
		max-width: 470px;
		line-height: 1.5;
	}

	.load-error .button {
		margin-top: 4px;
	}

	@media (max-width: 900px) {
		.table-scroll {
			overflow-x: auto;
		}

		table {
			min-width: 790px;
		}
	}

	@media (max-width: 700px) {
		.page-heading {
			align-items: flex-start;
		}

		table,
		tbody,
		tr,
		td {
			display: block;
			width: 100%;
		}

		.table-scroll {
			overflow: visible;
		}

		table {
			min-width: 0;
		}

		thead {
			display: none;
		}

		tbody tr {
			padding: 10px 15px;
			border-top: 1px solid #edf0f4;
		}

		td {
			display: grid;
			grid-template-columns: 112px minmax(0, 1fr);
			align-items: center;
			gap: 9px;
			padding: 7px 0;
			border: 0;
		}

		td::before {
			content: attr(data-label);
			color: #8995a5;
			font-size: 9px;
			font-weight: 700;
		}

		.row-actions {
			justify-content: flex-start;
		}
	}

	@media (max-width: 500px) {
		.page-heading {
			align-items: flex-start;
			flex-direction: column;
		}

		.page-heading > .button {
			width: 100%;
		}

		.field-grid {
			grid-template-columns: 1fr;
		}

		.form-card {
			padding: 18px 15px;
		}

		.list-heading {
			align-items: flex-start;
			padding: 17px 15px;
		}

		.list-tools {
			align-items: flex-end;
			flex-direction: column;
			gap: 7px;
		}

		td {
			grid-template-columns: 95px minmax(0, 1fr);
		}

		.alert-info {
			flex-wrap: wrap;
		}
	}
</style>
