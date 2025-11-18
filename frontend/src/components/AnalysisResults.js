import {
  Paper,
  Box,
  Group,
  SimpleGrid,
  List,
  Text,
  Title as MantineTitle
} from '@mantine/core';
import ReactMarkdown from 'react-markdown'; 
import JobCard from './JobCard';
import SkillTag from './SkillTag';

const MarkdownRenderer = ({ text }) => {
  return (
    <ReactMarkdown
      components={{
        p: ({ children }) => <Text component="p" mb="sm">{children}</Text>,
        strong: ({ children }) => <Text span fw={700}>{children}</Text>,
      }}
    >
      {text || ''} 
    </ReactMarkdown>
  );
};


function AnalysisResults({ results }) {
  
  const recommendation = results?.recommendation || {};
  const details = results?.analysis_details || {};
  const jobs = results?.top_jobs || [];

  return (
    <Box mt="xl">
      <Paper shadow="sm" p="lg" withBorder mb="lg" style={{ direction: 'rtl' }}>
        <MantineTitle order={3} c="blue.6" mb="sm">✨ ההמלצה של ה-AI</MantineTitle>     
        <MarkdownRenderer text={recommendation.opening} />
        <MarkdownRenderer text={recommendation.gap_analysis_intro} />
        <MantineTitle order={4} mt="lg" mb="sm">
          {recommendation.cv_review_title}
        </MantineTitle>
        <List withPadding>
          {(recommendation.cv_review_points || []).map((point, i) => (
            <List.Item key={i}>
              <MarkdownRenderer text={point} />
            </List.Item>
          ))}
        </List>
        <MarkdownRenderer text={recommendation.closing} />
      </Paper>
      <Paper shadow="sm" p="lg" withBorder mb="lg" style={{ direction: 'rtl' }}>
        <MantineTitle order={3} c="grape.6" mb="md">📊 ניתוח כישורים</MantineTitle>
        <MantineTitle order={5} mb="sm">הכישורים שלך:</MantineTitle>
        <Group mb="md" style={{ flexWrap: 'wrap', justifyContent: 'flex-start' }}>
          {(details.cv_skills || []).map((skill) => (
            <SkillTag key={skill} skillName={skill} color="green" />
          ))}
        </Group>

        <MantineTitle order={5} mb="sm">פערים מול השוק:</MantineTitle>
        <Group style={{ flexWrap: 'wrap', justifyContent: 'flex-start' }}>
          {(details.market_gaps || []).map((skill) => (
            <SkillTag key={skill} skillName={skill} color="orange" />
          ))}
        </Group>
      </Paper>
      <MantineTitle order={3} mb="md">🔥 משרות שיכולות להתאים עבורך</MantineTitle>
      <SimpleGrid cols={{ base: 1, md: 2 }} spacing="lg">
        {jobs.map((job, index) => (
          <JobCard key={index} job={job} />
        ))}
      </SimpleGrid>
      
    </Box>
  );
}

export default AnalysisResults;