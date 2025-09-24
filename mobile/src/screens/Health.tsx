import React from "react";
import { View, Text, ActivityIndicator, StyleSheet, ScrollView } from "react-native";
import { useQuery } from "@tanstack/react-query";
import { apiGet } from "../lib/apiClient";
import { useI18n } from "../i18n";

type HealthBody = { status?: string; service?: string; checks?: Record<string, string> };

export default function Health() {
  const { t } = useI18n();

  const q = useQuery({
    queryKey: ["healthz"],
    queryFn: async () => {
      const { data, headers } = await apiGet<HealthBody>("/healthz");
      return { body: data, reqId: headers.get("x-request-id") };
    },
    staleTime: 5_000,
  });

  if (q.isLoading) return <ActivityIndicator style={{ marginTop: 32 }} />;
  if (q.isError) return (
    <View style={styles.card}><Text style={styles.title}>{t("health.title")}</Text>
      <Text style={styles.error}>{t("common.error")}: {(q.error as Error).message}</Text>
    </View>
  );

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <View style={styles.card}>
        <Text style={styles.title}>{t("health.title")}</Text>
        <Text style={styles.row}>{t("health.status")}: <Text style={styles.ok}>{q.data?.body?.status ?? "—"}</Text></Text>
        <Text style={styles.row}>{t("health.requestId")}: {q.data?.reqId ?? "—"}</Text>
        {q.data?.body?.service && <Text style={styles.row}>service: {q.data.body.service}</Text>}
        {q.data?.body?.checks && (
          <View style={{ marginTop: 8 }}>
            {Object.entries(q.data.body.checks).map(([k, v]) => (
              <Text style={styles.row} key={k}>{k}: {v}</Text>
            ))}
          </View>
        )}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { padding: 16 },
  card: { backgroundColor: "#fff", borderRadius: 16, padding: 16, shadowOpacity: 0.1, shadowRadius: 8 },
  title: { fontSize: 20, fontWeight: "600", marginBottom: 8 },
  row: { fontSize: 16, marginTop: 4 },
  ok: { color: "green", fontWeight: "600" },
  error: { color: "crimson", fontWeight: "600" },
});