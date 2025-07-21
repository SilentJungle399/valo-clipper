<template>
	<n-config-provider :theme="darkTheme">
		<n-message-provider>
			<div class="root">
				<div class="container">
					<InputForm></InputForm>
					<YTVideo></YTVideo>
					<ClipWindow></ClipWindow>
				</div>
			</div>
		</n-message-provider>
	</n-config-provider>
</template>

<script setup lang="ts">
import { darkTheme, NConfigProvider, NMessageProvider } from "naive-ui";
</script>

<style>
body {
	background-color: #121212;
	color: white;
}

.root {
	display: flex;
	justify-content: center;
	margin-top: 50px;
}

.container {
	display: flex;
	flex-direction: column;
	gap: 20px;
}
</style>
