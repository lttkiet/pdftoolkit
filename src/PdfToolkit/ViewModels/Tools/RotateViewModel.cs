using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using PdfSharp.Pdf;
using PdfSharp.Pdf.IO;
using PdfToolkit.Services;

namespace PdfToolkit.ViewModels.Tools;

public partial class RotateViewModel : ViewModelBase
{
    private readonly MainWindowViewModel _mainVm;

    [ObservableProperty]
    private string _pageRange = string.Empty;

    [ObservableProperty]
    private string _selectedAngle = "90";

    public RotateViewModel(MainWindowViewModel mainVm)
    {
        _mainVm = mainVm;
    }

    public List<string> Angles { get; } = ["90", "180", "270"];

    [RelayCommand]
    private async Task RotateAsync()
    {
        string? sourcePath;

        if (_mainVm.DocumentModel.IsOpen)
        {
            sourcePath = _mainVm.DocumentModel.FilePath;
        }
        else
        {
            sourcePath = await _mainVm.FileDialogService.OpenPdfAsync(GetWindow());
        }

        if (sourcePath == null)
        {
            _mainVm.StatusText = "No PDF file selected";
            return;
        }

        if (!int.TryParse(SelectedAngle, out var angle))
        {
            _mainVm.StatusText = "Invalid angle";
            return;
        }

        var savePath = await _mainVm.FileDialogService.SavePdfAsync(GetWindow(), "rotated.pdf");
        if (savePath == null) return;

        try
        {
            using var srcDoc = PdfReader.Open(sourcePath, PdfDocumentOpenMode.Import);

            var pagesToRotate = string.IsNullOrWhiteSpace(PageRange)
                ? Enumerable.Range(0, srcDoc.PageCount).ToHashSet()
                : PageRangeParser.Parse(PageRange, srcDoc.PageCount).ToHashSet();

            using var result = new PdfDocument();
            foreach (var page in srcDoc.Pages)
            {
                var imported = result.AddPage(page);
                imported.Rotate = 0;
            }

            for (var i = 0; i < result.PageCount; i++)
            {
                if (pagesToRotate.Contains(i))
                    result.Pages[i].Rotate = (result.Pages[i].Rotate + angle) % 360;
            }

            result.Save(savePath);
            _mainVm.StatusText = $"Rotated {pagesToRotate.Count} pages by {angle}°";
        }
        catch (Exception ex)
        {
            _mainVm.StatusText = $"Rotate failed: {ex.Message}";
        }
    }
}
