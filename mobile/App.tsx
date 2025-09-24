import React from "react";
import { SafeAreaView, View, Text, Button } from "react-native";
import { WithQuery } from "./src/lib/query";
import { I18nProvider, useI18n } from "./src/i18n";
import Health from "./src/screens/Health";

function Shell() {
  const { t, locale, setLocale } = useI18n();
  return (
    <SafeAreaView style={{ flex: 1 }}>
      <View style={{ padding: 16, borderBottomWidth: StyleSheet.hairlineWidth, borderColor: "#ddd", flexDirection: "row", justifyContent: "space-between", alignItems: "center" }}>
        <Text style={{ fontWeight: "700", fontSize: 18 }}>Layba Mobile</Text>
        <View style={{ flexDirection: "row", gap: 8 }}>
          <Button title="EN" onPress={() => setLocale("en")} />
          <Button title="UK" onPress={() => setLocale("uk")} />
          <Button title="PL" onPress={() => setLocale("pl")} />
        </View>
      </View>
      <Health />
    </SafeAreaView>
  );
}

export default function App() {
  return (
    <I18nProvider>
      <WithQuery>
        <Shell />
      </WithQuery>
    </I18nProvider>
  );
}
