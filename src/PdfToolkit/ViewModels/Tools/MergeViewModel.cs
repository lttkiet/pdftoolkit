using System.Collections.ObjectModel;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using PdfSharp.Pdf;
using PdfSharp.Pdf.IO;

namespace PdfToolkit.ViewModels.Tools;

public partial class MergeViewModel : ViewModelBase
{
    private readonly MainWindowViewModel _mainVm;

    public ObservableCollection<string> FileList { get; } = new();

    [ObservableProperty]
    private int _selectedIndex = -1;

    public MergeViewModel(MainWindowViewModel mainVm)
    {
        _mainVm = mainVm;
    }

    [RelayCommand]
    private async Task AddFilesAsync()
    {
        var paths = await _mainVm.FileDialogService.OpenMultiPdfAsync(GetWindow());
        foreach (var path in paths)
            FileList.Add(path);
    }

    [RelayCommand]
    private void Remove()
    {
        if (SelectedIndex >= 0 && SelectedIndex < FileList.Count)
            FileList.RemoveAt(SelectedIndex);
    }

    [RelayCommand]
    private void MoveUp()
    {
        if (SelectedIndex <= 0) return;
        var item = FileList[SelectedIndex];
        FileList.RemoveAt(SelectedIndex);
        FileList.Insert(SelectedIndex - 1, item);
        SelectedIndex--;
    }

    [RelayCommand]
    private void MoveDown()
    {
        if (SelectedIndex < 0 || SelectedIndex >= FileList.Count - 1) return;
        var item = FileList[SelectedIndex];
        FileList.RemoveAt(SelectedIndex);
        FileList.Insert(SelectedIndex + 1, item);
        SelectedIndex++;
    }

    [RelayCommand]
    private async Task MergeAsync()
    {
        if (FileList.Count == 0)
        {
            _mainVm.StatusText = "No files to merge";
            return;
        }

        var savePath = await _mainVm.FileDialogService.SavePdfAsync(GetWindow(), "merged.pdf");
        if (savePath == null) return;

        try
        {
            using var result = new PdfDocument();
            foreach (var path in FileList)
            {
                using var src = PdfReader.Open(path, PdfDocumentOpenMode.Import);
                foreach (var page in src.Pages)
                    result.AddPage(page);
            }
            result.Save(savePath);
            _mainVm.StatusText = $"Merged {FileList.Count} files ({result.PageCount} pages)";
        }
        catch (Exception ex)
        {
            _mainVm.StatusText = $"Merge failed: {ex.Message}";
        }
    }
}
