import { Card, Text, Title, Button, Group, Badge } from '@mantine/core';

function JobCard({ job }) {
  return (
    <Card shadow="sm" padding="lg" radius="md" withBorder h="100%" style={{ display: 'flex', flexDirection: 'column' }}>
      <Group justify="space-between" align="flex-start" mb="xs">
        <div style={{ flex: 1 }}>
          <Title order={4} style={{ lineHeight: 1.3 }}>{job.title}</Title>
          <Text size="sm" c="dimmed">
            {job.company}
          </Text>
        </div>
        <Badge color="teal" variant="light">
          {job.match_percentage}% התאמה
        </Badge>
      </Group>

      <Text size="sm" mb="md" style={{ flex: 1 }}>
        רמת ניסיון: <Text span fw={700}>{job.level}</Text>
      </Text>

      <Button
        variant="light"
        color="blue"
        fullWidth
        mt="auto"
        radius="md"
        component="a"
        href={job.link}
        target="_blank"
        rel="noopener noreferrer"
      >
        צפה במשרה
      </Button>
    </Card>
  );
}

export default JobCard;