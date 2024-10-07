<script lang="ts">
	import "./app.css";
	import Header from "./components/Header.svelte";
	import { Backend, type ProteinData, type TaxonomyInfo } from "./backend";
	import { onMount } from "svelte";
	import { Button, Textarea } from "flowbite-svelte";
	import {
		ArrowUpRightFromSquareOutline,
		ArrowUpRightFromSquareSolid,
	} from "flowbite-svelte-icons";
	import Select from "svelte-select";

	let sequence = `MMITFQCLIGILLIANNLAFDICKASNPRFCKCQSHSKMQCGSFEVTTNTINNLIIKCSMKSDVNEISKIFLNVIEGENIDTAEVILENCLIVHDFNWYLPIFIVSGRELPFWLTISKRYEVYLYYLRAIETLESLTLSMINTLVIGSKAFDINPYLKTLRIKNNNFVKLDAKNPFWGLHNLEILEISKNKKVVFGREPFFLLPKLKILYLDNNNLESIPDKLFFGLDSLTDLVLSGNRIKSLTDESFFGLIMSLKRIDLKGNRLQKTEIDKIHKYFGDEFILIDY`;
	let topK = 100;
	let results: ProteinData;
	let topKIdxs: number[];

	type SelectItem = { value: string; label: string; taxonomy: string };
	let items: SelectItem[] = [];
	let selectedFilters: SelectItem[] | undefined;

	$: isSequenceValid = validSequence(sequence);

	async function updateSearch(
		sequence: string,
		topK: number,
		selectedFilters: SelectItem[] | undefined
	) {
		let classFilters, phylumFilters;
		if (selectedFilters) {
			classFilters = selectedFilters
				.filter((d) => d.taxonomy === "class")
				.map((d) => d.value);
			phylumFilters = selectedFilters
				.filter((d) => d.taxonomy === "phylum")
				.map((d) => d.value);

			// don't filter if there are no filters, duh!
			if (classFilters.length === 0) classFilters = undefined;
			if (phylumFilters.length === 0) phylumFilters = undefined;
		}

		console.log(classFilters, phylumFilters);
		results = await Backend.computeSimilarity({
			sequence: sequence.toUpperCase(),
			topK,
			classFilters,
			phylumFilters,
		});
		topKIdxs = sortedIdxs(results);
	}

	onMount(async () => {
		await updateSearch(sequence, topK, selectedFilters);

		const taxonomyInfo = await Backend.taxonomyInfo();
		items = parseTax(taxonomyInfo);
	});

	function validSequence(s: string) {
		if (s.length === 0) return false;

		const l = s.toUpperCase();
		const validAA = new Set("*ACDEFGHIKLMNPQRSTVWY");
		return Array.from(l).every((d) => validAA.has(d));
	}

	function sortedIdxs(results: ProteinData) {
		const s = results.similarity.map((d, i) => [d, i]);
		const sorted = s.sort((a, b) => b[0] - a[0]);
		return sorted.map((d) => d[1]);
	}

	function parseTax(t: TaxonomyInfo) {
		const label = (categeory: string, item: string) =>
			`${item} [${categeory}]`;
		const classesItems = t.classes.map((d) => ({
			value: d,
			label: label("class", d),
			taxonomy: "class",
		}));
		const phylumItems = t.phyla.map((d) => ({
			value: d,
			label: label("phylum", d),
			taxonomy: "phylum",
		}));
		return classesItems.concat(phylumItems);
	}
</script>

<Header />

<main class="p-5">
	<div class="mb-10">
		<div class="mb-2">
			<b>Protein Sequence</b> (input/query)
		</div>
		<Textarea bind:value={sequence} rows={4} />
		<div class="mt-2 mb-4">
			<div class="mb-2">
				<b>Filter</b>
			</div>
			<div style="">
				<Select
					{items}
					placeholder="Filter by Class or Phylum"
					multiple
					bind:value={selectedFilters}
				/>
			</div>
		</div>
		<Button
			color="dark"
			disabled={!isSequenceValid}
			on:click={async () => {
				topK = 100;
				await updateSearch(sequence, topK, selectedFilters);
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
				{@const taxonomyClass = results.ncbiTaxonomyClass[i]}
				{@const taxonomyPhylum = results.ncbiTaxonomyPhylum[i]}
				{@const _function = results.function[i]}
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
							<div><b>Class:</b> {taxonomyClass ?? "-"}</div>
							<div><b>Phylum:</b> {taxonomyPhylum ?? "-"}</div>
							<div>
								<b>Sequence Length:</b>
								{sequenceLength}
							</div>
							<div>
								<b>Cosine Similarity:</b>
								{similarity.toFixed(2)}
							</div>
							<div
								style="max-height: 100px; overflow-y: scroll; "
							>
								<b>Function:</b>
								{_function}
							</div>
						</div>
						<div></div>
					</div>
				</div>
			{/each}
		</div>
		<div class="flex justify-center m-5">
			{#if results && results.sequenceLength.length % 100 === 0}
				<Button
					color="alternative"
					on:click={async () => {
						topK += 100;
						await updateSearch(sequence, topK, selectedFilters);
					}}>Click to see more</Button
				>
			{/if}
		</div>
	{/if}
</main>

<style>
	.protein {
		outline: 1px solid rgba(255, 255, 255, 0.1);
		border-radius: 3px;
		width: 300px;
		padding: 15px;
	}
	.title {
		font-size: larger;
		font-weight: 500;
	}
</style>
