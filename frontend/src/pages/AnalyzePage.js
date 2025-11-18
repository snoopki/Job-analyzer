import { Container, LoadingOverlay } from '@mantine/core';
import { useAnalyzeCV } from '../hooks/useAnalyzeCV';
import Loader from '../components/Loader';
import CVInputForm from '../components/CVInputForm'; 
import AnalysisResults from '../components/AnalysisResults'; 

function AnalyzePage() {
  const { results, isLoading, error, analyze } = useAnalyzeCV();
  const handleSubmit = (cvText) => {
    analyze(cvText);
  };

  return (
    <Container size="md" style={{ direction: 'rtl', textAlign: 'right' }}>
      
      <LoadingOverlay
        visible={isLoading}
        overlayProps={{ radius: 'sm', blur: 2 }}
        loader={Loader}
        loaderProps={{ size: 'lg', type: 'dots' }}
        style={{ position: 'fixed', inset: 0, zIndex: 1000 }}
      />

      <CVInputForm 
        isLoading={isLoading} 
        onSubmit={handleSubmit} 
      />

      {results && !isLoading && !error && (
        <AnalysisResults results={results} />
      )}
    </Container>
  );
}

export default AnalyzePage;