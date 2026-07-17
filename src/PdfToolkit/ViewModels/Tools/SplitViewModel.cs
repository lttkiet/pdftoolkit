using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using PdfSharp.Pdf;
using PdfSharp.Pdf.IO;
using PdfToolkit.Services;

namespace PdfToolkit.ViewModels.Tools;

public partial class SplitViewModel : ViewModelBase
{
    private readonly MainWindowViewModel _mainVm;

    [ObservableProperty]
    private string _pageRange = string.Empty;

    public SplitViewModel(MainWindowViewModel mainVm)
    {
        _mainVm = mainVm;
    }

    [RelayCommand]
    private async Task ExtractAsync()
    {
        if (!_mainVm.DocumentModel.IsOpen)
        {
            _mainVm.StatusText = "No PDF open. Open a PDF first.";
            return;
        }

        if (string.IsNullOrWhiteSpace(PageRange))
        {
            _mainVm.StatusText = "Enter a page range (e.g. 1-3,5)";
            return;
        }

        var savePath = await _mainVm.FileDialogService.SavePdfAsync(GetWindow(), "split.pdf");
        if (savePath == null) return;

        try
        {
            var totalPages = _mainVm.DocumentModel.PageCount;
            var indices = PageRangeParser.Parse(PageRange, totalPages);

            if (indices.Count == 0)
            {
                _mainVm.StatusText = "No valid pages in range";
                return;
            }

            using var srcDoc = PdfReader.Open(_mainVm.DocumentModel.FilePath!, PdfDocumentOpenMode.Import);
            using var result = new PdfDocument();
            foreach (var i in indices)
                result.AddPage(srcDoc.Pages[i]);
            result.Save(savePath);
            _mainVm.StatusText = $"Extracted {result.PageCount} pages";
        }
        catch (Exception ex)
        {
            _mainVm.StatusText = $"Extract failed: {ex.Message}";
        }
    }
}
