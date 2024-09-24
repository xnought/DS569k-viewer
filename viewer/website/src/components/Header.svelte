<script lang="ts">
	import { Button } from "flowbite-svelte";
	import { GithubSolid, FilePdfSolid } from "flowbite-svelte-icons";

	const color = "alternative";
</script>

<nav>
	<div id="inner">
		<div class="left">
			<span id="title-desc" style="color:#D1E600;"
				>569k Protein Embeddings Search</span
			>
		</div>
		<div class="right">
			<Button
				size="xs"
				href="https://huggingface.co/datasets/donnyb/569k-protein-embeddings"
				target="_blank"
				{color}
				outline
				>Huggingface Dataset 🤗
			</Button>
			<!--
			<Button
				size="xs"
				href="https://arxiv.org/abs/2409.09011"
        target="_blank"
        {color}
        outline
				>Paper
				<FilePdfSolid size="md" class="ml-1" />
			</Button>
      -->
		</div>
	</div>
</nav>

<style>
	nav {
		background: rgba(0, 0, 0, 0.95);
	}
	#inner {
		padding: 10px;
		padding-left: 15px;
		display: flex;
		justify-content: space-between;
		height: 60px;
	}
	.left {
		display: flex;
		gap: 20px;
		align-items: center;
	}
	.right {
		/* position: fixed;
		top: 10px;
		right: 10px; */
	}
	#title-desc {
		font-size: 20px;
		font-weight: 250;
	}
	b {
		font-weight: 700;
	}
	/* #github {
		cursor: pointer;
	} */
</style>
