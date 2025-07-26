<template>
	<n-card v-if="currentMatch" style="max-width: 1200px">
		<n-flex style="gap: 20px" vertical>
			<n-flex style="gap: 30px">
				<n-flex vertical>
					<span style="font-weight: bold; color: #9ca3af">Global time offset:</span>
					<n-input-number v-model:value="globalOffset" style="max-width: 150px" />
				</n-flex>
				<n-flex vertical>
					<n-button
						tertiary
						@click="showRoundSelector = !showRoundSelector"
						style="margin-top: auto"
						>{{ showRoundSelector ? "Hide rounds" : "Show rounds" }}</n-button
					>
				</n-flex>
			</n-flex>
			<n-space v-if="showRoundSelector">
				<span style="font-weight: bold; color: #9ca3af">Set offset by kill:</span>
				<n-tabs type="line" animated>
					<n-tab-pane
						v-for="round in Object.keys(killsByRound)"
						:key="round"
						:name="`Round ${round} (${scores[parseInt(round)]?.join(' - ')})`"
					>
						<n-flex>
							<n-button
								v-for="kill in killsByRound[round]"
								:key="kill.time_in_match_in_ms"
								class="kill-button"
								@click="() => setOffset(kill)"
								ghost
							>
								<span
									:style="{
										paddingRight: '5px',
										fontWeight: 'bold',
										color:
											currentPlayerTeam === kill.killer.team
												? '#acd1af'
												: '#ff6961',
									}"
								>
									{{ getAgentByPuuid(kill.killer.puuid).name }}
									{{ kill.killer.puuid === profile.data.puuid ? "(me)" : "" }}
								</span>
								-
								<span
									:style="{
										paddingLeft: '5px',
										fontWeight: 'bold',
										color:
											currentPlayerTeam === kill.victim.team
												? '#acd1af'
												: '#ff6961',
									}"
								>
									{{ getAgentByPuuid(kill.victim.puuid).name }}
									{{ kill.victim.puuid === profile.data.puuid ? "(me)" : "" }}
								</span>
							</n-button>
						</n-flex>
					</n-tab-pane>
				</n-tabs>
			</n-space>
		</n-flex>
	</n-card>
</template>

<script setup lang="ts">
import { NCard, NFlex, NButton, NInputNumber, NTabs, NTabPane, NSpace } from "naive-ui";
import { useAccount, useSeekbar, usePlayer } from "~/store";

const accountStore = useAccount();
const seekbar = useSeekbar();
const player = usePlayer();

const currentMatch = ref();
const timeDiff = ref(0);
const killsByRound = ref<Record<string, any[]>>({});
const globalOffset = ref(0);
const scores = ref([[0, 0]]);
const currentPlayerTeam = ref("");
const showRoundSelector = ref(true);

const progress = computed(() => seekbar.progress);
const streamStart = computed(() => accountStore.matchList.start);
const profile = computed(() => accountStore.profile);

const matchList = computed(() => {
	return accountStore.matchList.matches.sort((a, b) => {
		return (
			new Date(a.metadata.started_at).getTime() - new Date(b.metadata.started_at).getTime()
		);
	});
});

const combineKillsbyRound = (kills: any[]) => {
	const killsByRound: Record<number, any[]> = {};
	kills.forEach((kill) => {
		if (!killsByRound[kill.round]) {
			killsByRound[kill.round] = [];
		}
		killsByRound[kill.round]!.push(kill);
	});
	return killsByRound;
};

const getAgentByPuuid = (puuid: string) => {
	return currentMatch.value.players.find((player: any) => player.puuid === puuid)?.agent;
};

const setOffset = (kill: any) => {
	if (!currentMatch.value || !currentMatch.value.kills || currentMatch.value.kills.length === 0) {
		return;
	}

	const killTime = kill.time_in_match_in_ms + timeDiff.value;
	const offsetValue = progress.value * 1000 - killTime;
	globalOffset.value = Math.floor(offsetValue) / 1000;
	showRoundSelector.value = false;
};

watch(
	() => progress.value,
	(newProgress) => {
		currentMatch.value = matchList.value.find((match) => {
			const matchStart = new Date(match.metadata.started_at).getTime();
			const matchEnd = matchStart + match.metadata.game_length_in_ms;
			const streamTime = new Date(streamStart.value).getTime() + newProgress * 1000;
			const found = streamTime >= matchStart && streamTime <= matchEnd;
			if (found) {
				timeDiff.value = matchStart - new Date(streamStart.value).getTime();
				killsByRound.value = combineKillsbyRound(match.kills);

				currentPlayerTeam.value = match.players.find(
					(player: any) => player.puuid === profile.value.data.puuid
				)?.team_id;

				match.rounds.forEach((round: any) => {
					if (round.winning_team === currentPlayerTeam.value) {
						const nScore = [
							scores.value[scores.value.length - 1]![0]! + 1,
							scores.value[scores.value.length - 1]![1]!,
						];
						scores.value.push(nScore);
					} else {
						const nScore = [
							scores.value[scores.value.length - 1]![0]!,
							scores.value[scores.value.length - 1]![1]! + 1,
						];
						scores.value.push(nScore);
					}
				});
			}
			return found;
		});
	},
	{ immediate: true }
);

watch(
	() => globalOffset.value,
	(newOffset) => {
		player.setOffset(newOffset);
	}
);

watch(currentMatch, (newMatch) => {
	console.log(newMatch);
	showRoundSelector.value = newMatch && newMatch.rounds && newMatch.rounds.length > 0;
});

onMounted(() => {
	// globalOffset.value = 102; // TODO REMOVE THIS
	// showRoundSelector.value = false; // TODO REMOVE THIS
});
</script>

<style></style>
