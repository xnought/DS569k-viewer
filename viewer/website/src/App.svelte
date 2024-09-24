<script lang="ts">
	import "./app.css";
	import Header from "./components/Header.svelte";
	import { Backend, type EmbeddingsData } from "./backend";
	import { onMount } from "svelte";
	import { Button, Textarea } from "flowbite-svelte";
	import {
		ArrowUpRightFromSquareOutline,
		ArrowUpRightFromSquareSolid,
	} from "flowbite-svelte-icons";

	let sequence = `MNKYSAFIVCISLVLLFTKKDVGSHNVDSRIYGFQQSSGICHIYNGTICRDVLSNAHVFVSPNLTMNDLEERLKAAYGVIKESKDMNANCRMYALPSLCFSSMPICRTPERTNLLYFANVATNAKQLKNVSIRRKRTKSKDIKNISIFKKKSTIYEDVFSTDISSKYPPTRESENLKRICREECELLENELCQKEYAIAKRHPVIGMVGVEDCQKLPQHKDCLSLGITIEVDKTENCYWEDGSTYRGVANVSASGKPCLRWSWLMKEISDFPELIGQNYCRNPGSVENSPWCFVDSSRERIIELCDIPKCADKIWIAIVGTTAAIILIFIIIFAIILFKRRTIMHYGMRNIHNINTPSADKNIYGNSQLNNAQDAGRGNLGNLSDHVALNSKLIERNTLLRINHFTLQDVEFLEELGEGAFGKVYKGQLLQPNKTTITVAIKALKENASVKTQQDFKREIELISDLKHQNIVCILGVVLNKEPYCMLFEYMANGDLHEFLISNSPTEGKSLSQLEFLQIALQISEGMQYLSAHHYVHRDLAARNCLVNEGLVVKISDFGLSRDIYSSDYYRVQSKSLLPVRWMPSESILYGKFTTESDVWSFGVVLWEIYSYGMQPYYGFSNQEVINLIRSRQLLSAPENCPTAVYSLMIECWHEQSVKRPTFTDISNRLKTWHEGHFKASNPEM`;
	let topK = 100;
	let results: EmbeddingsData;
	let topKIdxs;

	onMount(async () => {
		results = await Backend.computeSimilarity({
			sequence: sequence.toUpperCase(),
			topK,
		});
		topKIdxs = sortedIdxs(results);
	});

	function validSequence(s: string) {
		if (s.length === 0) return false;

		const l = s.toUpperCase();
		const validAA = new Set("*ACDEFGHIKLMNPQRSTVWY");
		return Array.from(l).every((d) => validAA.has(d));
	}

	function sortedIdxs(results: EmbeddingsData) {
		const s = results.similarity.map((d, i) => [d, i]);
		const sorted = s.sort((a, b) => b[0] - a[0]);
		return sorted.map((d) => d[1]);
	}
	$: isSequenceValid = validSequence(sequence);
</script>

<Header />

<main class="p-5">
	<div class="mb-10">
		<div class="mb-2">
			<b>Protein Sequence</b> (input/query)
		</div>
		<Textarea bind:value={sequence} rows={4} />
		<Button
			color="dark"
			disabled={!isSequenceValid}
			on:click={async () => {
				topK = 100;
				results = await Backend.computeSimilarity({
					sequence: sequence.toUpperCase(),
					topK,
				});
				topKIdxs = sortedIdxs(results);
			}}
		>
			{#if isSequenceValid}
				Query 569k Database
			{:else}
				Enter valid residues
			{/if}
		</Button>
	</div>
	{#if results}
		<div class="flex gap-5 flex-wrap">
			{#each topKIdxs as i}
				{@const accession = results.accession[i]}
				{@const similarity = results.similarity[i]}
				{@const proteinName = results.proteinName[i]}
				{@const organismName = results.organismName[i]}
				{@const sequenceLength = results.sequenceLength[i]}
				<div class="protein">
					<div>
						<div class="title">
							<Button
								size="xs"
								href="https://www.uniprot.org/uniprotkb/{accession}/entry"
								target="_blank"
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
								<b>Sequence Length:</b>
								{sequenceLength}
							</div>
							<div>
								<b>Cosine Similarity:</b>
								{similarity.toFixed(2)}
							</div>
						</div>
						<div></div>
					</div>
				</div>
			{/each}
		</div>
		<div class="flex justify-center m-5">
			<Button
				color="alternative"
				on:click={async () => {
					topK += 100;
					results = await Backend.computeSimilarity({
						sequence: sequence.toUpperCase(),
						topK,
					});
					topKIdxs = sortedIdxs(results);
				}}>Click to see more</Button
			>
		</div>
	{/if}
</main>

<style>
	a {
		color: slateblue;
	}
	.protein {
		outline: 1px solid grey;
		border-radius: 3px;
		width: 300px;
		padding: 15px;
	}
	.title {
		font-size: larger;
		font-weight: 500;
	}
</style>
