<template>
	<n-card>
		<n-slider v-model:value="value" range :step="1" />
	</n-card>
</template>

<script setup lang="ts">
import { NSlider, NCard } from "naive-ui";

const value = ref([0, 100]);
</script>
