<template>
	<n-config-provider :theme="darkTheme">
		<n-message-provider>
			<div class="container">
				<InputForm></InputForm>
			</div>
		</n-message-provider>
	</n-config-provider>
</template>

<script setup lang="ts">
import { darkTheme, NConfigProvider, NMessageProvider, useMessage } from "naive-ui";

// onMounted(() => {
// 	window.$message = useMessage();
// });
</script>

<style>
body {
	background-color: #1e1e1e;
	color: white;
}

.container {
	display: flex;
	justify-content: center;
	margin-top: 50px;
}
</style>
