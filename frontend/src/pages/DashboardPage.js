import React from 'react';
import {
  Container,
  Title,
  LoadingOverlay,
  Alert,
  Text,
  Box,
} from '@mantine/core';
import { IconAlertCircle } from '@tabler/icons-react';
import { useMarketData } from '../hooks/useMarketData';
import BarSkillsChart from '../components/charts/BarSkillsChart';
import ExperiencePieChart from '../components/charts/ExperiencePieChart';

export default function DashboardPage() {
  const { chartData, isLoading, error } = useMarketData();

  if (error && !chartData) {
    return (
      <Container>
        <Alert icon={<IconAlertCircle size="1rem" />} title="שגיאה!" color="red">
          {error}
        </Alert>
      </Container>
    );
  }

  return (
    <Container fluid style={{ paddingTop: 16, paddingBottom: 24 }}>
      <Title order={2} mb="md" align="center">
        דשבורד מגמות שוק
      </Title>

      {error && chartData && (
        <Alert icon={<IconAlertCircle size="1rem" />} title="שגיאת רענון" color="yellow" mb="md">
          לא הצלחנו לרענן את הנתונים. ייתכן שהנתונים המוצגים אינם עדכניים. ({error})
        </Alert>
      )}

      {chartData?.totalJobs > 0 && (
        <Text align="center" mb="lg">
          מתוך <b>{chartData.totalJobs}</b> משרות שנמצאו באתר Drushim-IL ניתן לראות כי:
        </Text>
      )}

      <LoadingOverlay visible={isLoading && !chartData} overlayProps={{ blur: 2 }} />

      {chartData && (
        <Box maw="75%" mx="auto">
          <BarSkillsChart data={chartData.skills} />
          <ExperiencePieChart data={chartData.levels} />
        </Box>
      )}
    </Container>
  );
}
