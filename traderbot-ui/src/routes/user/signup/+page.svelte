<script lang="ts">
	/** @type {import('./$types').PageData} */
	import { Button } from '$lib/components/ui/button';
	import * as AlertDialog from '$lib/components/ui/alert-dialog';
	import * as Breadcrumb from '$lib/components/ui/breadcrumb/index.js';
	import type { PageData } from './$types.js';
	import SettingsForm from './settings-form.svelte';

	export let data: PageData;
</script>

<SettingsForm data={data.form} />
