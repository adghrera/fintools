<script>
	/** @type {import('./$types').PageData} */
	export let data;
</script>

<svelte:head>
	<title>About</title>
	<meta name="description" content="About this app" />
</svelte:head>

<div class="text-column">
	<h1>This is just a slug page</h1>
	<p>Some content here {data.post.title}</p>
	<div>{@html data.post.content}</div>
</div>
