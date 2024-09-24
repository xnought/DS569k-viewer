<script lang="ts">
	import "./app.css";
	import Header from "./components/Header.svelte";
	import { Backend, type EmbeddingsData } from "./backend";
	import { onMount } from "svelte";
	import { Button } from "flowbite-svelte";
	import {
		ArrowUpRightFromSquareOutline,
		ArrowUpRightFromSquareSolid,
	} from "flowbite-svelte-icons";

	let sequence = `MNKYSAFIVCISLVLLFTKKDVGSHNVDSRIYGFQQSSGICHIYNGTICRDVLSNAHVFVSPNLTMNDLEERLKAAYGVIKESKDMNANCRMYALPSLCFSSMPICRTPERTNLLYFANVATNAKQLKNVSIRRKRTKSKDIKNISIFKKKSTIYEDVFSTDISSKYPPTRESENLKRICREECELLENELCQKEYAIAKRHPVIGMVGVEDCQKLPQHKDCLSLGITIEVDKTENCYWEDGSTYRGVANVSASGKPCLRWSWLMKEISDFPELIGQNYCRNPGSVENSPWCFVDSSRERIIELCDIPKCADKIWIAIVGTTAAIILIFIIIFAIILFKRRTIMHYGMRNIHNINTPSADKNIYGNSQLNNAQDAGRGNLGNLSDHVALNSKLIERNTLLRINHFTLQDVEFLEELGEGAFGKVYKGQLLQPNKTTITVAIKALKENASVKTQQDFKREIELISDLKHQNIVCILGVVLNKEPYCMLFEYMANGDLHEFLISNSPTEGKSLSQLEFLQIALQISEGMQYLSAHHYVHRDLAARNCLVNEGLVVKISDFGLSRDIYSSDYYRVQSKSLLPVRWMPSESILYGKFTTESDVWSFGVVLWEIYSYGMQPYYGFSNQEVINLIRSRQLLSAPENCPTAVYSLMIECWHEQSVKRPTFTDISNRLKTWHEGHFKASNPEM`;
	let topK = 30;
	let results: EmbeddingsData;
	let topKIdxs;

	onMount(async () => {
		results = await Backend.computeSimilarity({
			sequence,
			topK,
		});
		topKIdxs = sortedIdxs(results);
	});

	function sortedIdxs(results: EmbeddingsData) {
		const s = results.similarity.map((d, i) => [d, i]);
		const sorted = s.sort((a, b) => b[0] - a[0]);
		return sorted.map((d) => d[1]);
	}
</script>

<Header />

<main class="p-5">
	<div class="flex gap-5 flex-wrap">
		{#if results}
			{#each topKIdxs as i}
				{@const accession = results.accession[i]}
				{@const similarity = results.similarity[i]}
				{@const proteinName = results.proteinName[i]}
				{@const organismName = results.organismName[i]}
				<div class="protein">
					<div>
						<div class="title">
							<Button
								size="xs"
								href="https://www.uniprot.org/uniprotkb/{accession}/entry"
								outline
								>{accession}
								<ArrowUpRightFromSquareOutline
									size="xs"
									class="ml-1"
								/></Button
							>
							{proteinName}
						</div>
						<div style="color: grey">
							<div><b>Organism:</b> {organismName}</div>
							<div>
								<b>Cosine Similarity:</b>
								{similarity.toFixed(2)}
							</div>
						</div>
						<div></div>
					</div>
				</div>
			{/each}
		{/if}
	</div>
</main>

<style>
	a {
		color: slateblue;
	}
	.protein {
		outline: 1px solid lightgrey;
		border-radius: 3px;
		width: 500px;
		padding: 15px;
	}
	.title {
		font-size: larger;
		font-weight: 500;
	}
</style>
