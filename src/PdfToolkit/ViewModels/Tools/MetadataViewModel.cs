using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using PdfSharp.Pdf;
using PdfSharp.Pdf.IO;

namespace PdfToolkit.ViewModels.Tools;

public partial class MetadataViewModel : ViewModelBase
{
    private readonly MainWindowViewModel _mainVm;

    [ObservableProperty]
    private string _title = string.Empty;

    [ObservableProperty]
    private string _author = string.Empty;

    [ObservableProperty]
    private string _subject = string.Empty;

    [ObservableProperty]
    private string _keywords = string.Empty;

    [ObservableProperty]
    private string _creator = string.Empty;

    [ObservableProperty]
    private string _producer = string.Empty;

    [ObservableProperty]
    private string _pageInfo = string.Empty;

    public MetadataViewModel(MainWindowViewModel mainVm)
    {
        _mainVm = mainVm;
    }

    [RelayCommand]
    private async Task ReloadAsync()
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

        try
        {
            using var doc = PdfReader.Open(sourcePath, PdfDocumentOpenMode.Modify);
            var info = doc.Info;

            Title = info.Title ?? string.Empty;
            Author = info.Author ?? string.Empty;
            Subject = info.Subject ?? string.Empty;
            Keywords = info.Keywords ?? string.Empty;
            Creator = info.Creator ?? string.Empty;
            Producer = info.Producer ?? string.Empty;
            PageInfo = $"Pages: {doc.PageCount}";

            _mainVm.StatusText = "Metadata loaded";
        }
        catch (Exception ex)
        {
            _mainVm.StatusText = $"Load metadata failed: {ex.Message}";
        }
    }

    [RelayCommand]
    private async Task SaveAsync()
    {
        string? sourcePath = null;

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

        var savePath = await _mainVm.FileDialogService.SavePdfAsync(GetWindow(), "metadata_updated.pdf");
        if (savePath == null) return;

        try
        {
            using var doc = PdfReader.Open(sourcePath, PdfDocumentOpenMode.Modify);

            doc.Info.Title = Title;
            doc.Info.Author = Author;
            doc.Info.Subject = Subject;
            doc.Info.Keywords = Keywords;
            doc.Info.Creator = Creator;

            doc.Save(savePath);
            _mainVm.StatusText = $"Metadata saved to {Path.GetFileName(savePath)}";
        }
        catch (Exception ex)
        {
            _mainVm.StatusText = $"Save metadata failed: {ex.Message}";
        }
    }
}
